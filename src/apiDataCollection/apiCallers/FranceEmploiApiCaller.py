from helpers.HttpCaller import HttpCaller, UnauthorizedException
from helpers.Oauth2Helper import Oauth2Helper
import json
import datetime
import sys
from pathlib import Path

FRANCE_TRAVAIL_FILE_NAME = "FRANCE_TRAVAIL_API"
ACCEPTED_CRITERAS = [
    "departement, publieeDepuis, maxCreationDate, minCreationData"]
JSON_KEYS = {  # (key,value) : (our keys, france_travail keys)
    "technical_id": "id",
    "place": "lieuTravail",
    "publication_date": "dateCreation",
    "actualisation_date": "dateActualisation",
    "rome_libelle": "romeLibelle",
    "appellation_libelle": "appellationlibelle",
    "contrat_type": "typeContrat",
    "experience": "experienceLibelle",
    "salary": "salaire",
    "sector": "secteurActiviteLibelle",
    "qualification": "qualificationLibelle"
}


class FranceEmploiApiCaller:
    """Class for calling the France Emploi APIs with OAth2 authentication
    Documentation here :
    Workflow to follow to use the France Travail Connect APIs : https://francetravail.io/data/documentation/comprendre-dispositif-pole-emploi-connect/open-id-connect
    APIs catalog : https://francetravail.io/data/api

    Raises:
        UnauthorizedException: if the request return 400 or 401

    """

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token"
        # TODO : mettre en paramètres si on veut utiliser une autre API de France Travail
        self.jobs_search_url = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
        self.access_token = ""

    def authenticate(self, scope: str, params: dict = {}):
        """get access_token to request France_Travail api

        Args:
            scope (str): specified scope from France_Travail api (in our case : api_offresdemploiv2 o2dsoffre)
            params (dict, optional): _description_. Defaults to {}.
        """
        # Function to get an access token via OAuth2 Grant Type
        # Documentation here :
        # - https://francetravail.io/data/documentation/utilisation-api-pole-emploi/generer-access-token
        self.access_token = Oauth2Helper.get_access_token_by_client_credential(
            access_token_url=self.access_token_url, scope=scope, client_id=self.client_id,
            client_secret=self.client_secret, params=params
        )

    def get_jobs_by_criterias(self, criteres: dict = {}) -> dict:
        """get jobs by specified criterias

        Args:
            criteres (dict, optional): list of criterias. Defaults to {}.

        Raises:
            UnauthorizedException: exit if HTTP response is 400 or 401

        Returns:
            dict: jobs
        """
        # Function to get jobs list by criterias
        # Documentation here :
        # - https://francetravail.io/data/api/offres-emploi?tabgroup-api=documentation
        # - https://francetravail.io/data/api/offres-emploi/documentation#/api-reference/operations/recupererListeOffre

        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json"
        }

        response = HttpCaller.get(
            url=self.jobs_search_url, headers=headers, params=criteres)

        # if Unauthorized response, raise exception
        if (response.status_code == 401 or response.status_code == 400):
            raise UnauthorizedException(response.content)

        return response


class DepartmentJobsCaller:
    """
    Class for retrieve jobs for a specific departement using FranceEmploiApiCaller
    Default range from France Emploi API to get a list of jobs is 150
    """

    def __init__(self, FranceEmploiApiCaller: FranceEmploiApiCaller, path="./",
                 **optionnals):
        """
        Iniatialize request for a specific search. Some arguments are optionnals

        Args:
            FranceEmploiApiCaller : calling the France Emploi APIs with OAth2 authentication
            path (string) : directory where the data will be stored
            departement (string) : representative of department in France
            publieeDepuis (int) :  1, 3, 7, 14 or 31
            maxCreationDate (string) : format yyyy-MM-dd'T'hh:mm:ss'Z'
            minCreationDate (string) : format yyyy-MM-dd'T'hh:mm:ss'Z')
        """
        assert (key in ACCEPTED_CRITERAS for key in optionnals.keys())
        self.FranceEmploiApiCaller = FranceEmploiApiCaller
        self.criteras = optionnals
        self.range_min = 0
        self.range_max = 149
        f_name = self.__create_file_name(self.criteras["departement"])
        self.json_file_path = Path(path) / f"{f_name}.json"

    def __create_file_name(self, department: str) -> str:
        """Create file name based on actual day :
        format Y_m_d_H_M_S_dep_FRANCE_TRAVAIL_API.json

        Args:
            department (_type_): department number

        Returns:
            str: file name
        """
        now = datetime.datetime.now()
        self.dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"{FRANCE_TRAVAIL_FILE_NAME}_dep{department}_{self.dt_string}"
        return file_name

    def __retrieve_number_of_jobs(self, header: dict) -> int:
        """ Retrieve number of jobs for one departement. This information is store
        in the header of HTTP response for GET request as
        'Content-Range': 'offres 0-149/3430', value is after /

        Args:
            header (dict): header of HTTP response

        Returns:
            int: total of jobs for specifics criteras
        """
        to_parse = header["Content-Range"]
        number_of_jobs = to_parse.split('/')[1]
        return int(number_of_jobs)

    def __store_value(self, result: dict, key: str):
        """Store value of the result["key"] if exist, else store None

        Args:
            result (dict): job in json format
            key (str): key

        Returns:
            _type_: Value or None
        """
        try:
            return result[key]
        except KeyError:
            return None

    def __store_json(self, json_data: dict, todump: list):
        """Store json_data into the file self.json_file_path

        Args:
            json_data (dict): job in json format
            todump (list): all jobs stored in a list
        """

        for res in json_data:
            cleaned_data = {}
            for (j_key, france_travail_key) in JSON_KEYS.items():
                cleaned_data[j_key] = self.__store_value(
                    res, france_travail_key)
            todump.append(cleaned_data)

    def get_jobs_by_department(self):
        """
        get all jobs based on the criteras passed on the creation of the instance
        """

        json_file = open(self.json_file_path, "w")
        total = 150
        json_response = ""
        json_todump = []

        # while all jobs not retrieve but < 3000 range
        while self.range_max < (min(total, 3000)):

            # update new range of jobs to download
            self.criteras["range"] = f"{str(self.range_min)}-{str(self.range_max)}"

            try:  # If exception raise, close the file and quit the program
                response = self.FranceEmploiApiCaller.get_jobs_by_criterias(
                    self.criteras)
            except UnauthorizedException:
                json_file.close()
                sys.exit(1)

            total = self.__retrieve_number_of_jobs(response.headers) - 1
            json_response = json.loads(response.text)
            self.__store_json(json_response["resultats"], json_todump)
            self.range_min = self.range_max + 1
            self.range_max = min(self.range_max+150, total)

        self.criteras.pop("range")
        data = {"results": json_todump,
                "metadata": {"request": self.criteras,
                             "date": self.dt_string}}
        json.dump(data, json_file, indent=4)
        json_file.close()
