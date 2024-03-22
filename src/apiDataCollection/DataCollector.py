from apiDataCollection.apiCallers.FranceEmploiApiCaller import FranceEmploiApiCaller
from apiDataCollection.apiCallers.MuseApiCaller import MuseApiCaller
import os


class DataCollector:
    # Class for collecting the data from their sources

    def __init__(self):
        pass

    @staticmethod
    def collect():
        print("Start of the step data collection")

        france_emploi_client_id = os.environ.get("FRANCE_EMPLOI_CLIENT_ID", "")
        france_emploi_client_secret = os.environ.get(
            "FRANCE_EMPLOI_CLIENT_SECRET", "")
        muse_client_secret = os.environ.get("MUSE_CLIENT_SECRET", "")
        if france_emploi_client_id == "":
            raise CredentialNotFoundException(
                "france_emploi_client_id environment variable not found")
        if france_emploi_client_secret == "":
            raise CredentialNotFoundException(
                "france_emploi_client_secret environment variable not found")
        if muse_client_secret == "":
            raise CredentialNotFoundException(
                "muse_client_secret environment variable not found")

        DataCollector.__collectFromFranceEmploi(
            france_emploi_client_id, france_emploi_client_secret)
        DataCollector.__collectFromMuse(muse_client_secret)

        print("Start of the step data collection")

    @staticmethod
    def __collectFromFranceEmploi(client_id: str, client_secret: str):
        print("Start of data collection for France Emploi")
        # Initialize the France Emploi API caller
        franceEmploi = FranceEmploiApiCaller(client_id, client_secret)

        # Authenticate to the France Emploi API services
        franceEmploi.authenticate("api_offresdemploiv2 o2dsoffre", {
                                  "realm": "/partenaire"})

        # Gets the jobs list with the criteria (=filter) on 'departement' with value '30'
        franceEmploiJobs = franceEmploi.get_jobs_by_criterias(
            {"departement": "30"})

        # Showing the first job from the obtained list
        print("Premier emploi depuis France Emploi: ",
              franceEmploiJobs['resultats'][0])

        print("End of data collection for France Emploi")

    @staticmethod
    def __collectFromMuse(client_secret: str):
        print("Start of data collection for Muse")

        # Initialize the Muse API caller
        muse = MuseApiCaller(client_secret)

        # Gets the jobs list with the criteria (=filter)
        list_all_jobs_parsed = list()
        for p in range(10):
            params = {"page": {p}, "descending": "true"}
            jobs_page = muse.get_jobs_by_criterias(params)
            jobs_parsed_list = muse.parse_job_from_page(jobs_page['results'])
            list_all_jobs_parsed = list_all_jobs_parsed + jobs_parsed_list

        print("End of data collection for Muse")


class CredentialNotFoundException(Exception):
    pass
