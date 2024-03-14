from helpers.HttpCaller import HttpCaller, UnauthorizedException
from helpers.Oauth2Helper import Oauth2Helper
import json
import datetime
import sys
from pathlib import Path

FRANCE_TRAVAIL_FILE_NAME = "FRANCE_TRAVAIL_API"


class FranceEmploiApiCaller:
    # Class for calling the France Emploi APIs with OAth2 authentication
    # Documentation here :
    # - Workflow to follow to use the France Travail Connect APIs : https://francetravail.io/data/documentation/comprendre-dispositif-pole-emploi-connect/open-id-connect
    # - APIs catalog : https://francetravail.io/data/api

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token"
        # TODO : mettre en paramètres si on veut utiliser une autre API de France Travail
        self.jobs_search_url = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
        self.access_token = ""

    def authenticate(self, scope: str, params: dict = {}):
        # Function to get an access token via OAuth2 Grant Type
        # Documentation here :
        # - https://francetravail.io/data/documentation/utilisation-api-pole-emploi/generer-access-token
        self.access_token = Oauth2Helper.get_access_token_by_client_credential(
            access_token_url=self.access_token_url, scope=scope, client_id=self.client_id,
            client_secret=self.client_secret, params=params
        )

    def get_jobs_by_criterias(self, criteres: dict = {}) -> dict:
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
            raise UnauthorizedException(response.message)

        return response


class DepartmentJobsCaller:
    """
    Class for retrieve jobs for a specific departement using FranceEmploiApiCaller
    Default range from France Emploi API to get a list of jobs is 150
    """

    def __init__(self, FranceEmploiApiCaller, department, path="."):
        self.FranceEmploiApiCaller = FranceEmploiApiCaller
        self.department = department
        self.range_min = 0
        self.range_max = 149
        f_name = self.__create_file_name(department, path)
        self.json_file_path = Path(path) / f"{f_name}.json"

    def __create_file_name(self, department, path):
        """
        Create file name based on actual day : format Y_m_d_H_M_S_dep_FRANCE_TRAVAIL_API.json
        """
        now = datetime.datetime.now()
        dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"{FRANCE_TRAVAIL_FILE_NAME}_dep{department}_{dt_string}"
        return file_name

    def __retrieve_number_of_jobs(self, header: dict):
        """
        Retrieve number of jobs for one departement. This information is store in the header of HTTP response for GET request as 
        'Content-Range': 'offres 0-149/3430', value is after /
        """

        to_parse = header["Content-Range"]
        number_of_jobs = to_parse.split('/')[1]
        return int(number_of_jobs)

    def __store_json(self, json_data, f):
        """
        Store json_data into the file self.json_file_path
        TODO : save only attributes needed
        """
        json.dump(json_data, f)

    def get_jobs_by_department(self):
        """
        Function to get all jobs for one specific departement
        """

        json_file = open(self.json_file_path, "w")
        total = 150

        while self.range_max < total:  # tant qu'on n'a pas reçu tous les jobs

            criteres = {
                "departement": self.department,
                "range": f"{str(self.range_min)}-{str(self.range_max)}"
            }

            try:  # If exception raise, close the file and quit the program
                response = self.FranceEmploiApiCaller.get_jobs_by_criterias(
                    criteres)
            except:
                json_file.close()
                sys.exit(1)

            # print(f"range_max = {self.range_max}")
            # print(f"total = {total}")
            total = self.__retrieve_number_of_jobs(response.headers) - 1

            json_response = json.loads(response.text)

            self.__store_json(json_response["resultats"], json_file)

            self.range_min = self.range_max + 1
            self.range_max = min(self.range_max+150, total)

        json_file.close()


def main():
    print("Hello World!")


if __name__ == "__main__":
    main()
