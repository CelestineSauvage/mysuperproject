from enum import Enum
import os


class MongoDBConstants(Enum):

    MONGO_ADMIN = os.getenv('MONGO_ADMIN')
    MONGO_ADMIN_PASS = os.getenv('MONGO_ADMIN_PASS')

    DB_NAME = 'jobmarket'
    JOB_COL_NAME = 'jobs'
    REGION_COL_NAME = 'region'
