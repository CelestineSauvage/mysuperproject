import helpers.MongoBddInfra as MongoBddInfra
import json
from pathlib import Path
from load.LoadConstants import MongoDBConstants

MONGO_USER = MongoDBConstants.MONGO_ADMIN.value
MONGO_PASS = MongoDBConstants.MONGO_ADMIN_PASS.value

DB_NAME = MongoDBConstants.DB_NAME.value
REGION_COL_NAME = MongoDBConstants.REGION_COL_NAME.value

if __name__ == "__main__":
    """
    Create collection in mongodb for store departments and regions.
    If already exists, remove and recreate.
    """

    client = MongoBddInfra.Mongodb(MONGO_USER, MONGO_PASS)
    # db
    is_db = client.is_database(DB_NAME)
    if is_db:
        db = client.client[DB_NAME]
    else:
        db = client.create_database(DB_NAME)

    # collection
    is_collection = client.is_collection(db, REGION_COL_NAME)
    if is_collection:
        col = db[REGION_COL_NAME]
        col.drop()
    col = client.create_collection(db, REGION_COL_NAME)

    with open(Path(__file__).parent / Path('load/dep.json')) as f:
        file_data = json.load(f)

    col.insert_many(file_data)
