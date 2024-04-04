import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from apiDataCollection.apiCallers.FranceEmploiApiCaller import \
    FranceEmploiApiCaller, DepartmentJobsCaller
from apiDataCollection.apiCallers.MuseApiCaller import MuseApiCaller
from apiDataCollection.apiCallers.AdzunaApiCaller import AdzunaApiCaller
from apiDataCollection.scraper.ApecScraper import ApecScraper
from apiDataCollection.APIConstants import DataCollectorConstants
from helpers.Chronometer import Chronometer
from apiDataCollection import JobsProcess

import logging
logger = logging.getLogger(__name__)


class FTDataCollector:

    global ARG_DATE_MIN, ARG_DATE_MAX, ARG_PUBLISHED_SINCE, ARG_DEPARTMENTS, \
        ARG_PATH, FT_CLIENT_ID, FT_CLIENT_SECRET

    ARG_DATE_MIN = DataCollectorConstants.ARG_DATE_MIN.value
    ARG_DATE_MAX = DataCollectorConstants.ARG_DATE_MAX.value
    ARG_PUBLISHED_SINCE = DataCollectorConstants.ARG_PUBLISHED_SINCE.value
    ARG_DEPARTMENTS = DataCollectorConstants.ARG_DEPARTMENTS.value
    ARG_PATH = DataCollectorConstants.ARG_PATH.value

    FT_CLIENT_ID = DataCollectorConstants.FT_CLIENT_ID.value
    FT_CLIENT_SECRET = DataCollectorConstants.FT_CLIENT_SECRET.value

    def _collect_from_france_emploi(self) -> FranceEmploiApiCaller:
        """Collect id and secret for france travail API 

        Returns:
            _type_: _description_
        """
        # Retrieve from environments variables
        france_emploi_client_id = os.environ.get(FT_CLIENT_ID, "")
        france_emploi_client_secret = os.environ.get(
            FT_CLIENT_SECRET, "")
        if france_emploi_client_id == "" or france_emploi_client_secret == "":
            raise CredentialNotFoundException(
                "environments variables for france travail not found")

        logger.info("Start of data collection for France Emploi")

        # Initialize the France Emploi API caller
        franceEmploi = FranceEmploiApiCaller(
            france_emploi_client_id, france_emploi_client_secret)

        # Authenticate to the France Emploi API services
        franceEmploi.authenticate("api_offresdemploiv2 o2dsoffre", {
            "realm": "/partenaire"})

        return franceEmploi

    def _parse_date(self, kwargs: dict) -> dict:
        """_summary_

        Args:
            kwargs (dict): args 

        Raises:
            ValueError: _description_

        Returns:
            dict: _description_
        """
        # Check for min date and max
        keys_date = [ARG_DATE_MIN, ARG_DATE_MAX]
        dates_formated = {}

        for key in keys_date:
            if kwargs[key] is not None:
                str_date = kwargs[key]

                # convert input string into iso format
                try:
                    tmp_date = datetime.strptime(
                        str_date, '%Y-%m-%dT%H:%M')
                    dates_formated[key] = tmp_date.strftime(
                        '%Y-%m-%dT%H:%M:%SZ')
                except ValueError as e:
                    logger.error(f"Wrong format for {key}", e)
                    sys.exit(1)

        # remove olds strings
        kwargs.pop(ARG_DATE_MIN)
        kwargs.pop(ARG_DATE_MAX)

        # update with isoformat string
        kwargs.update(dates_formated)
        return kwargs

    def _parse_department(self, kwargs: dict) -> list:
        """_summary_

        Args:
            kwargs (dict): _description_

        Returns:
            list: _description_
        """
        # if department not specified
        if (kwargs[ARG_DEPARTMENTS] is None):
            int_departments = list(range(1, 96, 1))
            int_departments.remove(20)  # Corse
            # format with 2digit
            departments = [(f"{number:02d}")
                           for number in int_departments]
            departments += ["971", "972", "973", "974", "976"]

        else:
            # take departments specified in input
            departments = kwargs[ARG_DEPARTMENTS].split()
        return departments

    def download(self, kwargs: dict):
        """_summary_

        Args:
            kwargs (dict): _description_
        """
        try:
            france_emploi = self._collect_from_france_emploi()
        except CredentialNotFoundException as ex:
            logger.error(ex)

        directory = Path(kwargs[ARG_PATH])
        # create directory if doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
        kwargs.pop(ARG_PATH)

        # return one or a list of departments
        departments = self._parse_department(kwargs)
        kwargs.pop(ARG_DEPARTMENTS)

        # transform date format TODO : error request
        kwargs = self._parse_date(kwargs)

        try:
            for dep in departments:
                logger.info(f"Departement {dep}")
                departement_download = DepartmentJobsCaller(
                    france_emploi,
                    path=directory,
                    departement=dep,
                    **kwargs)
                try:
                    departement_download.get_jobs_by_department()
                except requests.exceptions.RequestException:
                    pass
        except KeyboardInterrupt:  # SIG INT
            sys.exit()

        transformation = JobsProcess.FTJobsProcess()
        transformation.process_directory(directory
                                         )


class DataCollector:
    # Class for collecting the data from their sources

    france_emploi_client_id = ""
    france_emploi_client_secret = ""
    muse_client_secret = ""
    adzuna_api_id = ""
    adzuna_api_key = ""
    chrono = Chronometer()

    def __init__(self):
        pass

    @staticmethod
    def collectCredentialFromEnvVars():
        DataCollector.france_emploi_client_id = os.environ.get(
            "FRANCE_EMPLOI_CLIENT_ID", "")
        DataCollector.france_emploi_client_secret = os.environ.get(
            "FRANCE_EMPLOI_CLIENT_SECRET", "")
        DataCollector.muse_client_secret = os.environ.get(
            "MUSE_CLIENT_SECRET", "")
        DataCollector.adzuna_api_id = os.environ.get("ADZUNA_API_ID", "")
        DataCollector.adzuna_api_key = os.environ.get("ADZUNA_API_KEY", "")

        if DataCollector.france_emploi_client_id == "":
            raise CredentialNotFoundException(
                "FRANCE_EMPLOI_CLIENT_ID environment variable not found")
        if DataCollector.france_emploi_client_secret == "":
            raise CredentialNotFoundException(
                "FRANCE_EMPLOI_CLIENT_SECRET environment variable not found")
        if DataCollector.muse_client_secret == "":
            raise CredentialNotFoundException(
                "MUSE_CLIENT_SECRET environment variable not found")
        if DataCollector.adzuna_api_id == "":
            raise CredentialNotFoundException(
                "ADZUNA_API_ID environment variable not found")
        if DataCollector.adzuna_api_key == "":
            raise CredentialNotFoundException(
                "ADZUNA_API_KEY environment variable not found")

    @staticmethod
    def collect():
        print("Start of the step data collection")

        # DataCollector.__collectFromFranceEmploi()
        # DataCollector.__collectFromMuse()
        # DataCollector.__collectFromAdzuna()
        DataCollector.__collectFromApec()

        print("End of the step data collection")

    @staticmethod
    def __collectFromMuse():
        print("Start of data collection for Muse")

        # Initialize the Muse API caller
        muse = MuseApiCaller(DataCollector.muse_client_secret)

        # Gets the jobs list with the criteria (=filter)
        list_all_jobs_parsed = list()
        for p in range(10):
            params = {"page": {p}, "descending": "true"}
            jobs_page = muse.get_jobs_by_criterias(params)
            jobs_parsed_list = muse.parse_job_from_page(jobs_page['results'])
            list_all_jobs_parsed = list_all_jobs_parsed + jobs_parsed_list

        print("End of data collection for Muse")

    @staticmethod
    def __collectFromAdzuna():
        Adzuna = AdzunaApiCaller(DataCollector.adzuna_api_id,
                                 DataCollector.adzuna_api_key)

        country = 'fr'
        page = 1
        critere = {
            'results_per_page': '50',
            'sort_by': 'date',
            'max_days_old': '1',
        }

        adzuna_jobs = Adzuna.get_jobs_by_criterias(
            country=country, page=page, criteres=critere)
        print(adzuna_jobs)
        #    suite job
        # r = requests.get(f'https://api.adzuna.com/v1/api/jobs/fr/search/1', params=query)
        # response = r.json()
        # nb_count = response['count']
        # nb_page = ceil(nb_count/50)

        # keys_value = set()

        # start_time = time.time()
        # all_jobs = []
        # for page in range(1,2000):
        #     print(page)
        #     r = requests.get(f'http://api.adzuna.com/v1/api/jobs/fr/search/{page}', params=query)
        #     response = r.json()
        #     all_jobs.extend(response['results'])

        #     with open('all_jobs_22mars.json', 'w') as f:
        #         json.dump(all_jobs, f)

        #     df = pd.DataFrame(all_jobs)
        #     df.to_csv("all_jobs_22mars.csv")

        # print(len(all_jobs))

        # with open('all_jobs.json', 'w') as f:
        #     json.dump(all_jobs, f)

        # df = pd.DataFrame(all_jobs)
        # df.to_csv("all_jobs.csv")

        # print("Start of the step data collection")

        # ['__CLASS__', 'adref', 'category', 'company', 'contract_time', 'contract_type', 'created', 'description', 'id', 'latitude', 'location', 'longitude', 'redirect_url', 'salary_is_predicted', 'salary_max', 'salary_min', 'title']

        # query = {'app_id': adzuna_client_id,
        #     'app_key': adzuna_client_secret,
        #     'content-type': 'application/json',
        #     'results_per_page': '50', # max 50
        #     'sort_by': 'date',
        #     'max_days_old': '1',
        # }

    @staticmethod
    @chrono.timeit
    def __collectFromApec():
        print("Start of data collection for Apec")

        # Initialize the Apec scraper
        apecScraper = ApecScraper()

        # Gets the jobs list with the criteria (=filter)
        params = {"descending": "true", "sortsType": "DATE"}
        apecScraper.get_jobs_by_criterias(params)

        # Close the Apec scraper
        apecScraper.close_scraper()

        print("End of data collection for Apec")


class CredentialNotFoundException(Exception):
    pass
