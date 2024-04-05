from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid
from datetime import datetime, timezone
import sys
from pathlib import Path
import json

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

    @staticmethod
    def process_file_for_db_insertion(file, collection_name):

        # log.debug('process_file_for_db_insertion')
        jobs_list = Mongodb.get_jobs_from_file(file)
        Mongodb.insert_jobs_into_db(jobs_list, collection_name)

    @staticmethod
    def get_jobs_from_file(file):
        # log.debug('get_jobs_from_file')
        content_file_str = file.read_text()
        content_file_json = json.loads(content_file_str)

        return content_file_json

    @staticmethod
    def insert_jobs_into_db(jobs, collection_name):
        # log.debug('insert_jobs_into_db')
        for job in jobs:
            
            job = Mongodb.parse_and_clean_job(job)
            
            toto = Mongodb.insert_job(job, collection_name)
        
        return

    @staticmethod
    def parse_and_clean_job(job):
        # log.debug('parse_and_clean_job')
        # convert str to datetime
        try:
            job['contents']['publication_date'] = datetime.fromisoformat(job['contents']['publication_date'])
            job['contents']['actualisation_date'] = datetime.fromisoformat(job['contents']['actualisation_date'])
        except:
            pass

        #add _id
        job['_id'] = str(job['technical_id']) + "_" + str(job['source'])
        
        # add inserteed_date
        job['inserted_date'] = datetime.now(timezone.utc)
            
        return job

    @staticmethod
    def insert_job(job, collection_name):
        # log.debug('insert_job')
        toto = collection_name.update_one({'_id': job['_id']}, {'$set': job}, upsert=True)
        
        return toto


def database_check():
    print('database_check')
    jobs_schema_validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["technical_id", "inserted_date", "source", "contents"],
                "properties": {
                    "technical_id": {
                        "bsonType": "string",
                        "description":  "must be a string and is required"
                    },
                    "inserted_date": {
                        "bsonType": "date",
                        "description": "must be the date of database insertion"
                    },
                    "source": {
                        "bsonType": "int",
                        "enum": [0, 1],
                        "description": "can only be one of the enum values and is required"
                    },
                    "contents": {
                        "bsonType": "object",
                        "description": "nested document with 2 required element: title and publication_date",
                        "required": ["title", "publication_date"],
                        "properties": {
                            "title": {
                                "bsonType": "string",
                                "description": "must be a string and is required"
                            },
                            "publication_date": {
                                "bsonType": "date",
                                "description": "must be the date of database insertion"
                            }
                        }
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
    
    return None

def insert_new_data_into_db():
    print('insert_new_date_into_db')
    client = Mongodb("admin", "pass")
    db_name = 'test'
    collection_name = 'collection_job_test_with_shema_validation'

    db = client.create_or_connect_database(db_name)
    jobs_collection = db[collection_name]
    
    current_dir = Path.cwd()
    files_path_to_process = [p for p in current_dir.glob('data/data_to_insert/*.json') if p.is_file()]

    for file_path in files_path_to_process[0:10]:
        print(f"File under process: {file_path}")
        Mongodb.process_file_for_db_insertion(file_path, jobs_collection)
        print(f"File processed")



def question_data():
    print('question_data')
    # start_date = datetime(2024, 4, 4, 0, 0, 0, 0)
    # jobs.count_documents({})
    # len(list(jobs.find({"source" :0})))
    # list(
    #     jobs.find({
    #         'contents.publication_date' : {'$gte':start_date}
    #     })
    # )


    # jobs.find({"$source" :0})


    # # get taille of jos ccollection
    # print()


if __name__ == "__main__":
    main()
