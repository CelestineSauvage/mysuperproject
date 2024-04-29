
import logging
import json
from bson.json_util import dumps

from fastapi import FastAPI, HTTPException, status
from load import MongoBddInfra

from unidecode import unidecode
import re

from .FastApiConstants import FastApiConstants


# security = HTTPBasic()

# setup logger

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# load bdd

DB_NAME = "jobmarket"
JOB_NAME = 'job'
REGION = 'region'

# TODO a changer
MONGO_USER = 'admin'
MONGO_PASS = 'pass'

MOINS_1_AN = FastApiConstants.MOINS_1_AN.value
EXP_1_4 = FastApiConstants.EXP_1_4.value

REGION_LIST = FastApiConstants.REGION_LIST.value

# create app

app = FastAPI(
    title="jobmarket API",
    description="API to requests to mongoDB",
    openapi_tags=[
        {
            'name': 'Listing',
            'description': 'Listing'
        },
        {
            'name': 'Department',
            'description': 'functions that return data for department'
        },
        {
            'name': 'Region',
            'description': 'functions that return data for region'
        }]
)

# constants
MAX_DEP = 20
MAX_CATEGORY = 5

client = MongoBddInfra.Mongodb(MONGO_USER, MONGO_PASS)
db = client.client[DB_NAME]
col_jobs = db[JOB_NAME]
col_region = db[REGION]


def _process_string(val: str):
    val = unidecode(val)
    val = val.lower()  # lower case
    val = re.sub('[^0-9a-zA-Z]+', ' ', val)
    return val


def _search_by_town(town: str):
    p_town = _process_string(town)
    return {"contents.place.town ": f"{p_town}"}


def _search_by_department(dep: str):
    return {"contents.place.department": f"{dep}"}


def _search_by_region(reg: str):
    if reg not in REGION_LIST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Region code must be in {REGION_LIST}."
        )
    result = list(col_region.aggregate([
        {"$match": {"region.code": f"{reg}"}}
    ]))
    deps = [x["code"] for x in result]
    return {"contents.place.department": {"$in": deps}}


def query_groupby(groupby: str, number: str, limit=10, place: str = "dep"):
    """request to mongodb stat from department

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    if place == "reg":
        filter = _search_by_region(number)
    else:
        filter = _search_by_department(number)
    return list(col_jobs.aggregate([
        {"$match": filter},
        {"$group": {"_id": f'${groupby}', "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]))


def search_string_in_department(title: str, number: str):
    expr = re.compile(f"{_process_string(title)}")
    return list(col_jobs.aggregate([
        {"$match": {
            "$and": [
                _search_by_department(number),
                {
                    "$or": [
                        {"contents.title": expr},
                        {"contents.description": expr},
                        {"contents.category": expr}
                    ]}
            ]
        }}
    ]))


@ app.get("/jobmarket/department/{number:int}/search", tags=['Department'])
async def stat_search_department(search, number):
    result = str(len(search_string_in_department(search, number)))
    return {"result": result}


@ app.get("/jobmarket/department/{number:int}/category", tags=['Department'])
async def stat_category_department(number):
    result = query_groupby(
        "contents.category", number, MAX_CATEGORY)
    json_result = {"department": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/department/{number}/town", tags=['Department'])
async def stat_town_department(number):
    """returns the MAX_DEP towns with the most job offers

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    result = query_groupby("contents.place.town", number, MAX_DEP)
    json_result = {"department": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/region/{number}/town", tags=['Region'])
async def stat_town_region(number):
    """returns the MAX_DEP towns with the most job offers

    Args:
        number (_type_): region number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    result = query_groupby("contents.place.town", number, MAX_DEP, place="reg")
    json_result = {"region": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/department/{number}/experience", tags=['Department'])
async def stat_exp_department(number):
    """returns the numbers of jobs which required less than a year, one to 4 year et more 4 years experience

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    r_result = query_groupby("contents.experience", number)
    result = {"moins_1_an": 0,
              "exp_1_4_an": 0,
              "exp_4_an": 0}
    for sub in r_result:
        if sub["_id"] in MOINS_1_AN:
            result["moins_1_an"] += sub["count"]
        elif sub["_id"] in EXP_1_4:
            result["exp_1_4_an"] += sub["count"]
        else:
            result["exp_4_an"] += sub["count"]
    json_result = {"department": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/department/{number}/contract", tags=['Department'])
async def stat_contract_department(number):
    """returns the MAX_DEP towns with the most job offers

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    result = query_groupby("contents.contrat_type", number)
    for sub in result:
        if sub['_id'] is None:
            sub['_id'] = "non precise"
            break
    json_result = {"department": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/region", tags=['Listing'])
async def get_list_region():
    """returns the list of region

    Returns:
        json: [
                {
                    "code": int,
                    "libelle": str
                }
                }
    """
    result = list(col_region.aggregate([
        {
            "$project": {
                "_id": 0,
                "code": "$region.code",
                "libelle": "$region.libelle"
            }
        }
    ]))
    return list({v['code']: v for v in result}.values())


@ app.get("/jobmarket/departments", tags=['Listing'])
async def get_list_departments():
    """returns the list of departments and region

    Returns:
        json: [
                {
                    "code": int,
                    "libelle": str,
                    "region": {
                        "code": int,
                        "libelle": str
                    }
                }
    """
    return list(col_region.aggregate([
        {
            "$project": {
                "_id": 0,
                "code": 1,
                "libelle": 1
            }
        }
    ]))
