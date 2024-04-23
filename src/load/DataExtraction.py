import logging
from load import MongoBddInfra
import pandas as pd
from datetime import datetime
import re

level = 'INFO'
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=level)
logger = logging.getLogger(__name__)

db_name = "jobmarket"
job_col_name = 'job'


def check_database_heath() -> bool:
    """ Check if everything is OK to check data-base health (db + collection)

    Returns:
        bool: True : all is OK. False: something is not OK
    """
    logger.info(check_database_heath)
    client = MongoBddInfra.Mongodb("admin", "pass")
    is_db = client.is_database(db_name)
    if is_db:
        db = client.client[db_name]
        is_collection = client.is_collection(db, job_col_name)
        if is_db & is_collection:
            return True
        else:
            return False
    else:
        return False


def connect_collection():
    if check_database_heath():
        client = MongoBddInfra.Mongodb("admin", "pass")
        db = client.client[db_name]
        col = db[job_col_name]
        return col
    else:
        raise Exception("f{job_col_name} is not accessible")


def test():
    logger.info('test_data_extraction')
    col = connect_collection()

    ########################################################
    # min max des heures intégrés
    min_max_publication_date = \
    list(col.aggregate([
        {
            "$group": {
                '_id': '$source',
                "minPublicationDate": {"$min": "$contents.publication_date"},
                "maxPublicationDate": {"$max": "$contents.publication_date"}
            }
        }
    ]))

    ########################################################
    # Nombre d'offre par jours spécifique à chaque site. # Nombre d'offre par jours sur les x derniers jours?
    start_date = datetime(2024, 3, 30, 0, 0, 0, 0)
    test = list(col.aggregate([
        {"$match": {
            "contents.publication_date": {'$gte': start_date}
            }
        },
        { "$project": {
            "source": 1,
            "publiDate": {"$dateToString": {"date": "$contents.publication_date", "format": '%Y-%m-%d'}}
            }
        },
        { "$group": {
                "_id": {"source": "$source", "publiDate": "$publiDate"},
                "nb_job": {"$sum": 1}
            }
        },
        { "$project": {
                "_id": 0,
                "source": "$_id.source",
                "publiDate": "$_id.publiDate",
                "nb_job": 1
            }
        },
        {"$sort": {"publiDate": 1}}
    ]))

    df_test = pd.DataFrame(test)

    ########################################################
    # Nombre d'offre par jours en fonction du type de contrat
    test = list(col.aggregate([
        {
            "$group": {"_id": "$contents.contrat_type", "nb_job": {"$sum": 1}}
        },
        {
            "$project": {
                "_id": 0,
                "contrat_type": "$_id",
                "nb_job": 1
            }
        },
        { "$sort": {"nb_job": -1}}
    ]))
    df_test = pd.DataFrame(test)

    ########################################################
    # les offres avec "Data engineer" -> stat sur des métiers comme ça (modifié)
    value1 = 'Data Engineer'

    value2 = 'Data Analyste'
    expr = re.compile(f"{value1.lower()}|{value2.lower()}")
    test4 = list(col.aggregate([
        {"$addFields": {
            "title_cleaned": {"$toLower": "$contents.title"},
            "description_cleaned": {"$toLower": "$contents.description"},
            "category_cleaned": {"$toLower": "$contents.category"}
        }},
        {"$match": {
            "$or": [
                {"title_cleaned": expr},
                {"description_cleaned": expr},
                {"category_cleaned": expr}
            ]
        }},
        {"$unset": ["title_cleaned", "description_cleaned", "category_cleaned"]}
    ]))
        
        

    # stat par région/département/grandes villes ?

    list(col.aggregate([
        {
            "$project": {
                "_id": 0,
                "test": "$contents.place"
            }
        }
    ]))



# genre par compétence par exemple ?
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


