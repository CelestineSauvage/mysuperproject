import helpers.MongoBddInfra as MongoBddInfra
import json
from pathlib import Path

MONGO_USER = "admin"
MONGO_PASS = "pass"

DB_NAME = "jobmarket"
JOB_COL_NAME = 'region'

if __name__ == "__main__":

    client = MongoBddInfra.Mongodb(MONGO_USER, MONGO_PASS)
    # db
    is_db = client.is_database(DB_NAME)
    if is_db:
        db = client.client[DB_NAME]
    else:
        db = client.create_database(DB_NAME)

    # collection
    is_collection = client.is_collection(db, JOB_COL_NAME)
    if is_collection:
        col = db[JOB_COL_NAME]
        col.drop()
    col = client.create_collection(db, JOB_COL_NAME)

    with open(Path(__file__).parent / Path('dep.json')) as f:
        file_data = json.load(f)

    col.insert_many(file_data)
