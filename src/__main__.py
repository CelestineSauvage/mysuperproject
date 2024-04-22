from apiDataCollection.DataCollector import DataCollector
from mongoDBGestion import DataInsertion

#DataCollector.collectCredentialFromEnvVars()
DataCollector.collect()

DataInsertion.load_to_db()
print('out')
