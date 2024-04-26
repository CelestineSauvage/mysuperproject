from typing import Annotated, Optional
from pydantic import BaseModel

import logging
import pandas as pd
import json
from functools import partial

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from load import MongoBddInfra


# security = HTTPBasic()

# setup logger

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# load bdd

DB_NAME = "jobmarket"
JOB_COL_NAME = 'job'

MONGO_USER = "admin"
MONGO_PASS = "pass"

client = MongoBddInfra.Mongodb(MONGO_USER, MONGO_PASS)
db = client.client[DB_NAME]
col = db[JOB_COL_NAME]

# create app

app = FastAPI(
    title="jobmarket API",
    description="API to requests to mongoDB"
)

# constants
MAX_DEP = 20


def process_query_department(number):
    """request to mongodb stat from department

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    return list(col.aggregate([
        {"$match": {"contents.place.department": f"{number}"}},
        {"$group": {"_id": '$contents.place.town', "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": MAX_DEP}
    ]))


@ app.get("/jobmarket/department/{number}")
async def stat_department(number):
    """returns the MAX_DEP towns with the most job offers

    Args:
        number (_type_): department number

    Returns:
        list: [{town1 : count1}, {town2 : count2} ... ]
    """
    return process_query_department(number)
