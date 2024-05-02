
import logging

from fastapi import FastAPI
from helpers import MongoBddInfra
from helpers.LoadConstants import MongoDBConstants
from .FastApiQuery import JobQuery
from .FastApiConstants import FastApiConstants


from contextlib import asynccontextmanager
import os

# security = HTTPBasic()

# setup logger

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# query limit
MAX_DEP = 20
MAX_CATEGORY = 5

#
MOINS_1_AN = FastApiConstants.MOINS_1_AN.value
EXP_1_4 = FastApiConstants.EXP_1_4.value

# initiate query class
job_query = None

MONGO_HOST = MongoDBConstants.MONGO_HOST.value
MONGO_USER = MongoDBConstants.MONGO_ADMIN.value
MONGO_PASS = MongoDBConstants.MONGO_ADMIN_PASS.value

DB_NAME = MongoDBConstants.DB_NAME.value
REGION_COL_NAME = MongoDBConstants.REGION_COL_NAME.value
JOB_COL_NAME = MongoDBConstants.JOB_COL_NAME.value


@asynccontextmanager
async def lifespan(app: FastAPI):
    # BEFORE FASTAPI LAUNCHER

    # connect client to mongodb
    client = MongoBddInfra.Mongodb(MONGO_HOST, MONGO_USER, MONGO_PASS)

    # load 2 collections

    db = client.client[DB_NAME]
    col_jobs = db[JOB_COL_NAME]
    col_region = db[REGION_COL_NAME]
    global job_query
    job_query = JobQuery(col_jobs, col_region)
    yield

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
        }],
    lifespan=lifespan
)


@ app.get("/jobmarket/department/{number:int}/search", tags=['Department'])
async def stat_search_department(search, number):
    result = str(len(job_query.search_string_in_department(search, number)))
    return {"result": result}


@ app.get("/jobmarket/department/{number:int}/category", tags=['Department'])
async def stat_category_department(number):
    result = job_query.query_groupby(
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
    result = job_query.query_groupby("contents.place.town", number, MAX_DEP)
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
    result = job_query.query_groupby(
        "contents.place.town", number, MAX_DEP, place="reg")
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
    r_result = job_query.query_groupby("contents.experience", number)
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
    result = job_query.query_groupby("contents.contrat_type", number)
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
    return job_query.region_list()


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
    return job_query.department_list()
