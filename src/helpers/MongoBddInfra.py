from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, CollectionInvalid, OperationFailure
import sys
import logging


logger = logging.getLogger(__name__)


class NoSchemasValidation(Exception):
    pass


class Mongodb:
    def __init__(self, username, password):
        logger.debug('Initiate Mongodb instane')

        self.host = "127.0.0.1"
        self.port = 27017
        self.username = username
        self.password = password

        self.init_connection()

        self.check_client_connection()

        logger.info("Client connection created")

    def init_connection(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        logger.debug("init_connection")
        self.client = MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        return None

    def check_client_connection(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        logger.debug("check_client_connection")
        try:
            self.client.server_info()
            logger.info("MongoDB client is reachable")
            logger.info(self.client)
            return True
        except ConnectionFailure as e:
            sys.exit(f"check_client_connection ERROR:\n{e}")
        except OperationFailure as e:
            sys.exit(f"check_client_connection ERROR:\n{e}")

    def is_database(self, db_name: str) -> bool:
        """_summary_

        Args:
            db_name (str): _description_

        Returns:
            bool: _description_
        """
        logger.debug("is_database")
        is_db = db_name in self.client.list_database_names()
        return is_db

    def create_database(self, db_name: str):
        """_summary_

        Args:
            db_name (str): _description_

        Returns:
            _type_: _description_
        """
        logger.debug("create_database")
        try:
            db = self.client[db_name]
            logger.info(f'dataBase created : {db}')
            return db
        except Exception as e:
            raise (f"create_or_connect_database didn't work. \n Error : {e}")

    @staticmethod
    def is_collection(db, col: str) -> bool:
        logger.debug("is_collection")
        is_col = col in db.list_collection_names()
        return is_col

    @staticmethod
    def create_collection(db, collection_name: str, schema_validator=None):
        """_summary_

        Args:
            db (_type_): _description_
            collection_name (str): _description_
            validator (_type_, optional): _description_. Defaults to None.
        """
        logger.debug("create_database")
        try:
            coll = db.create_collection(collection_name)

            db.command("collMod", collection_name, validator=schema_validator)

            if schema_validator:
                Mongodb.check_shema_collection_creation(db, collection_name)

            logger.info(f'Collection Created : {coll}')
            return coll

        except Exception as e:
            sys.exit(f"Error occur during create_collection. Error : \n {e}")

    @staticmethod
    def check_shema_collection_creation(db: object, collection_name: str):
        """_summary_

        Args:
            db (object): 'pymongo.database.Database _description_
            collection_name (str): _description_

        Raises:
            NoSchemasValidation: _description_
        """
        logger.debug("check_shema_collection_creation")
        try:
            shemas = db.get_collection(f'{collection_name}').options()
            if not shemas:
                raise NoSchemasValidation(
                    f'Schema Validation : empty for {collection_name}')
        except NoSchemasValidation as e:
            sys.exit(
                f"Error occur during check_shema_collection_creation. Error: \n {e}")
