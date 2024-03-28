import logging
from abc import ABC, abstractmethod
import tempfile
from pathlib import Path
from apiDataCollection.APIConstants import FTConstants
import json
from unidecode import unidecode
import re

JSON_KEYS = FTConstants.JSON_KEYS.value
HOMOGENIZED_JOBS = FTConstants.HOMOGENIZED_JOBS.value

logger = logging.getLogger(__name__)


class JobsProcess(ABC):

    @abstractmethod
    def write_jobs(self, file: Path) -> tempfile.TemporaryFile:
        """write jobs list into a tmp json for mongodb

        Args:
            file (Path): _description_
        """
        pass

    @abstractmethod
    def process_job(self, job: dict) -> dict:
        """_summary_

        Args:
            job (dict): _description_
        """
        pass

    @abstractmethod
    def process_file(self, source_file: Path) -> list:
        pass

    @abstractmethod
    def __check_file(self, json_file: Path) -> bool:
        pass

    def process_directory(self, dir: Path):
        json_files = list(dir.glob('**/*.json'))
        for json_file in json_files:
            if self.__check_file(json_file):
                self.process_file(json_file)


FRANCE_TRAVAIL_FILE_NAME = FTConstants.FRANCE_TRAVAIL_FILE_NAME.value


class FTJobsProcess(JobsProcess):

    def __init__(self) -> None:
        pass

    def write_jobs(self, file: Path):
        return super().process_job(file)

    def _process_place(self, job: dict) -> dict:
        """format localisation in FT : "CODE DEPARTEMENT - COMMUNE"

        "place" : {
            "department" : str
            "town" : str
            }
        Args:
            job (dict): _description_

        Returns:
            dict: _description_
        """
        dep, town = (job["place"]["libelle"].split('-'))
        dep = dep[:-1]  # remove space
        town = town[1:]
        job["place"] = {"town": town,
                        "department": dep}
        return job

    def _process_activity(self, job: dict) -> dict:
        ft_tag = job["sector"]
        for (job_tag, val) in HOMOGENIZED_JOBS.items():
            if val == ft_tag:
                job["sector"] = job_tag
                break
        return job
        # logger.info(f"Job {job["technical_id"]} \
        #             activity is not in the default list")

    def _process_string(self, job: dict) -> dict:
        for j_key, value in job.items():
            if value is str:
                # change non-ASCII characters
                job[j_key] = unidecode(job[j_key])
                job[j_key] = job[j_key].lower()  # lower case
                job[j_key] = re.sub('[^0-9a-zA-Z]+', '*', job[j_key])
        return job

    def process_job(self, job: dict) -> dict:
        new_job = job
        new_job = self._process_activity(new_job)
        new_job = self._process_place(new_job)
        new_job = self._process_string(new_job)
        return new_job

    def process_file(self, source_file: Path) -> list:
        f = open('data.json')
        json_jobs_raw = json.load(f)["results"]
        json_jobs_cleaned = list(map(self.process_job, json_jobs_raw))
        return json_jobs_cleaned

    def __check_file(self, file: Path):
        return file.starswith(FRANCE_TRAVAIL_FILE_NAME)


class ApecJobsProcess(JobsProcess):

    def __init__(self) -> None:
        pass

    def write_jobs(self, file: Path):
        return super().process_job(file)

    def _process_place(self, job: dict) -> dict:
        """format localisation in Apec : "COMMUNE - CODE DEPARTEMENT"

        "place" : {
            "department" : str
            "town" : str
            }
        Args:
            job (dict): _description_

        Returns:
            dict: _description_
        """
        town, dep = (job["place"].split('-'))
        town = town[1:]
        dep = dep[:-1]  # remove space
        job["place"] = {"town": town,
                        "department": dep}
        return job

    def _process_activity(self, job: dict) -> dict:
        ft_tag = job["sector"]
        for (job_tag, val) in HOMOGENIZED_JOBS.items():
            if val == ft_tag:
                job["sector"] = job_tag
                break
        return job
        # logger.info(f"Job {job["technical_id"]} \
        #             activity is not in the default list")

    def _process_string(self, job: dict) -> dict:
        for j_key, value in job.items():
            if value is str:
                # change non-ASCII characters
                job[j_key] = unidecode(job[j_key])
                job[j_key] = job[j_key].lower()  # lower case
                job[j_key] = re.sub('[^0-9a-zA-Z]+', '*', job[j_key])
        return job

    def process_job(self, job: dict) -> dict:
        new_job = job
        new_job = self._process_activity(new_job)
        new_job = self._process_place(new_job)
        new_job = self._process_string(new_job)
        return new_job

    def process_file(self, source_file: Path) -> list:
        f = open('data.json')
        json_jobs_raw = json.load(f)["results"]
        json_jobs_cleaned = list(map(self.process_job, json_jobs_raw))
        return json_jobs_cleaned

    def __check_file(self, file: Path):
        return file.starswith(FRANCE_TRAVAIL_FILE_NAME)
