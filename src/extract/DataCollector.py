import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from extract.apiCallers.FranceEmploiApiCaller import \
    FranceEmploiApiCaller, DepartmentJobsCaller
from extract.scraper.ApecScraper import ApecScraper
from extract.APIConstants import DataCollectorConstants, ApecConstants, FTConstants
from helpers.Chronometer import Chronometer

import logging
logger = logging.getLogger(__name__)
chrono = Chronometer()
ARG_PATH = DataCollectorConstants.ARG_PATH.value


class FTDataCollector:

    global ARG_DATE_MIN, ARG_DATE_MAX, ARG_PUBLISHED_SINCE, ARG_DEPARTMENTS, \
        ARG_PATH, FT_CLIENT_ID, FT_CLIENT_SECRET

    ARG_DATE_MIN = DataCollectorConstants.ARG_DATE_MIN.value
    ARG_DATE_MAX = DataCollectorConstants.ARG_DATE_MAX.value
    ARG_PUBLISHED_SINCE = DataCollectorConstants.ARG_PUBLISHED_SINCE.value
    ARG_DEPARTMENTS = DataCollectorConstants.ARG_DEPARTMENTS.value

    FT_CLIENT_ID = DataCollectorConstants.FT_CLIENT_ID.value
    FT_CLIENT_SECRET = DataCollectorConstants.FT_CLIENT_SECRET.value

    @staticmethod
    @chrono.timeit
    def _collect_from_france_emploi() -> FranceEmploiApiCaller:
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

    @staticmethod
    @chrono.timeit
    def _parse_date(kwargs: dict) -> dict:
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

    @staticmethod
    @chrono.timeit
    def _parse_department(kwargs: dict) -> list:
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

    @staticmethod
    @chrono.timeit
    def collect(kwargs: dict):
        """_summary_

        Args:
            kwargs (dict): _description_
        """
        try:
            france_emploi = FTDataCollector._collect_from_france_emploi()
        except CredentialNotFoundException as ex:
            logger.error(ex)
            exit()

        directory = Path(kwargs[ARG_PATH])
        # create directory if doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
        kwargs.pop(ARG_PATH)

        # return one or a list of departments
        departments = FTDataCollector._parse_department(kwargs)
        kwargs.pop(ARG_DEPARTMENTS)

        # transform date format TODO : error request
        kwargs = FTDataCollector._parse_date(kwargs)

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


class ApecDataCollector:

    @staticmethod
    @chrono.timeit
    def collect(kwargs: dict):
        logger.info("Start of data collection for Apec")

        directory = Path(kwargs[ARG_PATH])
        # create directory if doesn't exist
        directory.mkdir(parents=True, exist_ok=True)
        kwargs.pop(ARG_PATH)

        if kwargs[ARG_PUBLISHED_SINCE] is None:
            published_since = ApecConstants.ANCIENNETE_PUBLICATION.value['tout']
        else:
            published_since = ApecConstants.ANCIENNETE_PUBLICATION.value[
                kwargs[ARG_PUBLISHED_SINCE]]

        # Initialize the Apec scraper
        apecScraper = ApecScraper(directory)

        # Gets the jobs list with the criteria (=filter)
        params = {"descending": "true", "sortsType": "DATE",
                  "anciennetePublication": published_since}

        apecScraper.get_jobs_by_criterias(params)

        # Close the Apec scraper
        apecScraper.close_scraper()

        logger.info("End of data collection for Apec")


class CredentialNotFoundException(Exception):
    pass
