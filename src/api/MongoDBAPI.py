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
JOB_COL_NAME = 'job'

# TODO a changer
MONGO_USER = "admin"
MONGO_PASS = "pass"

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
col = db[JOB_COL_NAME]


def _process_string(val: str):
    val = unidecode(val)
    val = val.lower()  # lower case
    val = re.sub('[^0-9a-zA-Z]+', ' ', val)
    return val


def process_query_department(groupby: str, number: str, limit=10):
    """request to mongodb stat from department

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    return list(col.aggregate([
        {"$match": {"contents.place.department": f"{number}"}},
        {"$group": {"_id": f'${groupby}', "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]))


def process_search_title_department(title: str, number: str):
    expr = re.compile(f"{_process_string(title)}")
    return list(col.aggregate([
        {"$match": {
            "$and": [
                {
                    "contents.place.department": f"{number}"
                },
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
async def stat_search(search, number):
    result = str(len(process_search_title_department(search, number)))
    return {"result": result}


@ app.get("/jobmarket/department/{number:int}/category")
async def stat_category(number):
    result = process_query_department(
        "contents.category", number, MAX_CATEGORY)
    json_result = {"department": number,
                   "result": result}
    return json_result


@ app.get("/jobmarket/department/{number}/town")
async def stat_department(number):
    """returns the MAX_DEP towns with the most job offers

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    result = process_query_department("contents.place.town", number, MAX_DEP)
    json_result = {"department": number,
                   "result": result}
    return json_result
