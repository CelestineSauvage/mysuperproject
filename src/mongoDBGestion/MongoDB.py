from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid
import sys

class NoSchemasValidation(Exception):
    pass

class Mongodb:
    def __init__(self, username, password):
        self.host="127.0.0.1"
        self.port=27017
        self.username=username
        self.password=password

        self.init_connection()

    def init_connection(self):
        try:
            # MongoClient('mongodb://username:password@hostnameOrReplicaset/?tls=True') replica by your own Service URI
            # uri = 'mongodb+srv://<username>:<password>@mongodb-e49d02ee-o2626ab53.database.cloud.ovh.net/admin?replicaSet=replicaset'
            self.client = MongoClient(
                    host=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            
            server_info = self.client.server_info()

            print("MongoDB cluster is reachable")
            print(self.client)
        except ConnectionFailure as e:
            print("Could not connect to MongoDB")
            sys.exit(e)
      
    def create_or_connect_database(self, db_name: str):
        """_summary_

        Args:
            db_name (str): _description_

        Returns:
            _type_: _description_
        """
        try:
            db = self.client[db_name]
        except Exception as e:
            raise (f"create_or_connect_database didn't work. \n Error : {e}")

        return db


    @staticmethod
    def create_collection(db, collection_name: str, schema_validator=None):
        """_summary_

        Args:
            db (_type_): _description_
            collection_name (str): _description_
            validator (_type_, optional): _description_. Defaults to None.
        """
        try:
            coll = db.create_collection(collection_name)
            
            db.command("collMod", collection_name, validator=schema_validator)
            
            if schema_validator:
                Mongodb.check_shema_collection_creation(db, collection_name)
                
        except Exception as e:
            sys.exit(f"Error occur during create_collection. Error : \n {e}")

        return coll
        

    @staticmethod
    def check_shema_collection_creation(db: object, collection_name: str):
        """_summary_

        Args:
            db (object): 'pymongo.database.Database _description_
            collection_name (str): _description_

        Raises:
            NoSchemasValidation: _description_
        """
        try:
            shemas = db.get_collection(f'{collection_name}').options()
            if not shemas:
                raise NoSchemasValidation(f'Schema Validation : empty for {collection_name}')
        except NoSchemasValidation as e:
            sys.exit(f"Error occur during check_shema_collection_creation. Error: \n {e}")
 
    @staticmethod
    def insert_data_into_collection(collection: object, documents: dict):
        """_summary_

        Args:
            collection (object):  <class 'pymongo.collection.Collection'>
            documents (dict): _description_
        """
        try:
            collection.insert_many(documents)
        except Exception as e:
            sys.exit(e)

jobs_schema_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["title", "source", "publication_date", "technical_id"],
            "properties": {
                "title": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                },
                "technical_id": {
                    "bsonType": "string",
                    "description":  "must be a string and is required"
                },
                "publication_date": {
                    "bsonType": "date",
                    "description": "must be a date and is required"
                },
                "source": {
                    "bsonType": "int",
                    "enum": [0, 1],
                    "description": "can only be one of the enum values and is required"
                }
            }
        }
    }


client = Mongodb("admin", "pass")
db_name = 'test'
collection_name = 'collection_job_test_with_shema_validation'

db = client.create_or_connect_database(db_name)
if collection_name in db.list_collection_names():
    jobs_collection = db[collection_name]
else:
    jobs_collection = client.create_collection(db, collection_name, jobs_schema_validator)

collection_without = client.create_collection(db, "collection_job_test_without_shema_validation")

from datetime import datetime

doc = [{
    "_id":100,
    "title": "id_1_new",
    "technical_id": "new_test", 
    "publication_date": datetime(1990, 1, 3),
    "source": 1
    }, {
    "_id":101,
    "title": "id_22_new",
    "technical_id": "BBBBB", 
    "publication_date": datetime(1990, 1, 3),
    "source": "1"
    }, {
    "_id":102,
    "title": "id_22_new",
    "technical_id": "BBBBB", 
    "publication_date": datetime(1990, 1, 3),
    "source": 1
    }
    ]

doc1={
    "_id":10000,
    "title": "newwwwwwww",
    "technical_id": "newwwwww", 
    "publication_date": datetime(1990, 1, 10),
    "source": 0,
    "content":{'toto':'titi'}
    }
try:
    # insert manu document
    client.insert_data_into_collection(jobs_collection, doc1)
    # upsert 
    #  et si les colonnes 
    from time import time
start_time= time()
for i in range(1,100000,1):
    doc1={
        "_id":"2_u",
        "title": "2",
        "technical_id": "gfkjgfjkgjfkjk", 
        "publication_date": datetime(1990, 1, 31),
        "source": 0,
        }

    jobs_collection.update_one({ '_id' : '2_u'}, { '$set': doc1 }, {'$unset':{}}, upsert=True)
    jobs_collection.replace_one({ '_id' : '2_u'}, { 'replacement': doc1 }, upsert=True)
print('end')
stop_time=time()


# create_jobs_collection()
# # technical_id: int id dans la source   / obligatoire 
# # title: str intitule string  // obligatoire
# # source = int 0 : FT ou 1 : APEC
# # publication_date: format DateTime "2024-03-22T10:22:21.000Z",
# # actualisation_date: format DateTime ou None,
# # sector: enum tag ou None
# # contract_type: int 0 : CDD , 1 : CDI  (a voir ) ou None
# # contract_time : int 0 : temps plein , 1 : temps partiel ou None
# # experience: char ou None
# # salary: str ou None
# # description : str
# # competences : list str ou None
# # company : str ou None
# # place : 
# #  commune : str
# #  département : int
