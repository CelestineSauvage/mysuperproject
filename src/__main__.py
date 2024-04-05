from apiDataCollection.DataCollector import DataCollector
from mongoDBGestion import MongoDB
# DataCollector.collectCredentialFromEnvVars()
# DataCollector.collect()

# INSERT DOCUMENT
# MongoDB()


MongoDB.database_check()
MongoDB.insert_new_data_into_db()
MongoDB.question_data()


print('out')