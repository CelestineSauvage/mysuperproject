from typing import Annotated, Optional
from pydantic import BaseModel

import logging
import pandas as pd
import json
from functools import partial

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from load import MongoBddInfra

from unidecode import unidecode
import re


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

# create app

app = FastAPI(
    title="jobmarket API",
    description="API to requests to mongoDB"
)

# constants
MAX_DEP = 20
MAX_CATEGORY = 5

client = MongoBddInfra.Mongodb(MONGO_USER, MONGO_PASS)
db = client.client[DB_NAME]
col_jobs = db[JOB_NAME]


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


def _search_by_region(region: str):
    pass


def groupby_in_department(groupby: str, number: str, limit=10):
    """request to mongodb stat from department

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    return list(col_jobs.aggregate([
        {"$match": _search_by_department(number)},
        {"$group": {"_id": f'${groupby}', "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]))


def exp_in_department(number: str):
    list_num = range(1, 10)
    query_result = groupby_in_department("contents.experience", number)
    query_keys = query_result.key
    for el in list_num:
        if el in query_keys:
            pass


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


@ app.get("/jobmarket/department/{number:int}/search")
async def stat_search_department(search, number):
    result = str(len(search_string_in_department(search, number)))
    return {"result": result}


@ app.get("/jobmarket/department/{number:int}/category")
async def stat_category_department(number):
    result = groupby_in_department(
        "contents.category", number, MAX_CATEGORY)
    json_result = {"department": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/department/{number}/town")
async def stat_town_department(number):
    """returns the MAX_DEP towns with the most job offers

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    result = groupby_in_department("contents.place.town", number, MAX_DEP)
    json_result = {"department": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/department/{number}/contract")
async def stat_contract_department(number):
    """returns the MAX_DEP towns with the most job offers

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    result = groupby_in_department("contents.contrat_type", number)
    for sub in result:
        if sub['_id'] is None:
            sub['_id'] = "non precise"
            break
    json_result = {"department": number,
                   "result": result}
    return json_result
