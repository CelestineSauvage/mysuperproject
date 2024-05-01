from helpers import MongoBddInfra
from pathlib import Path
import json
from datetime import datetime, timezone
import logging
import sys
import os
from helpers.LoadConstants import MongoDBConstants

logger = logging.getLogger(__name__)

MONGO_USER = MongoDBConstants.MONGO_ADMIN.value
MONGO_PASS = MongoDBConstants.MONGO_ADMIN_PASS.value

DB_NAME = MongoDBConstants.DB_NAME.value
JOB_COL_NAME = MongoDBConstants.JOB_COL_NAME.value

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


def process_file_for_db_insertion(file: Path, collection) -> bool:
    """_summary_

    Args:
        file (Path): The Path of the file to process
        collection (_type_): MongoDb collection

    Raises:
        Exception: _description_

    Returns:
        bool: _description_
    """
    logger.debug("IN process_file_for_db_insertion function")
    try:
        jobs_list = get_jobs_from_file(file)
        if not jobs_list:
            raise Exception(f"No data to treat {file}")
        parse_and_insert_jobs_into_db(jobs_list, collection)
        return True
    except Exception as e:
        logger.info(e)
        return False


def get_jobs_from_file(file):
    logger.debug("IN get_jobs_from_file function")
    try:
        content_file_str = file.read_text()
        content_file_json = json.loads(content_file_str)
        return content_file_json
    except Exception as e:
        logger.info(f"get_jobs_from_file function : file ="
                    f"{file}, ERROR was :\n {e}")
        return False


def parse_and_insert_jobs_into_db(jobs: list, collection) -> None:
    logger.debug("IN insert_jobs_into_db function")
    for job in jobs:
        job_parsed = parse_and_clean_job(job)
        if not job_parsed:
            # STEP TO DO
            logger.debug('job should be send to error collection')
            pass
        else:
            result = insert_job(job_parsed, collection)

    return None


def parse_and_clean_job(job: dict) -> dict:
    logger.debug("IN parse_and_clean_job function")

    try:
        if 'publication_date' in job['contents'].keys():
            job['contents']['publication_date'] = datetime.fromisoformat(
                job['contents']['publication_date'])
        if 'actualisation_date' in job['contents'].keys():
            job['contents']['actualisation_date'] = datetime.fromisoformat(
                job['contents']['actualisation_date'])

        # add _id
        job['_id'] = str(job['technical_id']) + "_" + str(job['source'])

        # add inserteed_date
        job['inserted_date'] = datetime.now(timezone.utc)

        return job
    except Exception as e:
        sys.exit(f"Error during parse_and_clean_job,\n job_to_process ="
                 f"{job}\nerror is:{e}")


def insert_job(job, collection_name) -> None:
    logger.debug("IN insert_job function")
    try:
        result = collection_name.update_one(
            {'_id': job['_id']}, {'$set': job}, upsert=True)
        return None
    except Exception as e:
        # envoyer le job quelques part => job.error
        logger.debug(f"job under process {job}")
        sys.exit(f"Error occur during insert_job function. Error: \n {e}")


def load_to_db(data_folder):
    logger.info('load_to_db START FUNCTION')
    logger.debug('load_to_db START FUNCTION')

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
    else:
        col = client.create_collection(db, JOB_COL_NAME, jobs_schema_validator)

    current_dir = Path.cwd()
    files_path_to_process = [p for p in current_dir.glob(
        f'{data_folder}/*.json') if p.is_file()]

    for file_path in files_path_to_process:
        logger.info(f"file under process : {file_path}")
        result = process_file_for_db_insertion(file_path, col)
        if result:
            file_path.unlink()
        else:
            # envoyer le fichier quelques part => error_path
            pass
        logger.debug("File processed")

    logger.debug("load_to_db OUT")
