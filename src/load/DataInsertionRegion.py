import MongoBddInfra
import json

MONGO_USER = "admin"
MONGO_PASS = "pass"

DB_NAME = "jobmarket"
JOB_COL_NAME = 'region'

client = MongoBddInfra.Mongodb(MONGO_USER, MONGO_PASS)
db = client.client[DB_NAME]
col = db[JOB_COL_NAME]

with open('./dep.json') as f:
    file_data = json.load(f)

col.insert_many(file_data)
