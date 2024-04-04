import logging
from abc import ABC, abstractmethod
import tempfile
from pathlib import Path
from apiDataCollection.APIConstants import FTConstants
import json
from unidecode import unidecode
import re
import datetime

JSON_KEYS = FTConstants.JSON_KEYS.value
HOMOGENIZED_JOBS = FTConstants.HOMOGENIZED_JOBS.value
FRANCE_TRAVAIL_FILE_NAME = FTConstants.FRANCE_TRAVAIL_FILE_NAME.value
FRANCE_TRAVAIL_SOURCE = 0

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
    def _check_file(self, json_file: Path) -> bool:
        pass

    def process_directory(self, dir: Path):
        json_files = list(dir.glob('**/*.json'))
        for json_file in json_files:
            if self._check_file(json_file):
                logger.info(f"process json_file : {json_file}")
                self.process_file(dir, json_file)


FRANCE_TRAVAIL_FILE_NAME = FTConstants.FRANCE_TRAVAIL_FILE_NAME.value


class FTJobsProcess(JobsProcess):

    def __init__(self) -> None:
        pass

    def _create_file_name(self, source_file: Path) -> str:
        """Create file name based on actual day :
        format FRANCE_TRAVAIL_API_process_dep_X_Y_m_d_H_M_S_dep_.json

        Args:
            department (_type_): department number

        Returns:
            str: file name
        """
        raw_file_name = source_file.name
        # logger.debug(f"raw_file_name {raw_file_name}")
        process_file_name = raw_file_name.replace("raw", "process")
        # logger.debug(f"process_file_name {process_file_name}")
        return process_file_name

    def write_jobs(self, jobs: list, dir: Path, source_file: Path) \
            -> tempfile.TemporaryFile:
        # logger.debug(f"source {source_file}")
        process_file_name = self._create_file_name(source_file)
        # logger.debug(f"process_file_name {process_file_name}")
        process_file = dir / process_file_name
        # logger.debug(f"process_file {process_file}")
        f_descriptor = open(process_file, "w")
        json.dump(jobs, f_descriptor, indent=4)
        f_descriptor.close()
        # TODO : must return a temp file

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
        # logger.debug(job["place"]["libelle"])
        place = job["place"]["libelle"]
        dep = place[0:2]
        town = place[5:]
        job["place"] = {"town": town,
                        "department": dep}
        return job

    def _process_category(self, job: dict) -> dict:
        ft_tag = job["category"]
        nb_category = len(HOMOGENIZED_JOBS)-1
        for count, (job_tag, val) in enumerate(HOMOGENIZED_JOBS.items()):
            if val == ft_tag:
                job["sector"] = job_tag
                break
            if count == nb_category:
                logger.info(f"Job {job["category"]} \
                    activity is not in the default list")
        return job

    def _process_string(self, job: dict) -> dict:
        for j_key, value in job.items():
            if "date" not in j_key:
                if isinstance(value, dict):
                    job[j_key] = self._process_string(value)
                if isinstance(value, str):
                    # change non-ASCII characters
                    job[j_key] = unidecode(job[j_key])
                    job[j_key] = job[j_key].lower()  # lower case
                    job[j_key] = re.sub('[^0-9a-zA-Z]+', ' ', job[j_key])
        return job

    def _process_salary(self, job: dict) -> dict:
        if "salary" in job:
            if "libelle" in job["salary"]:
                logger.debug(f"Process salary {job["salary"]}")
                job["salary"] = job["salary"]["libelle"]
                return job
        job.pop("salary")
        return job

    def _process_experience(self, job: dict) -> dict:
        if job["experience"] is not None:
            experience_list = job["experience"].split()
            job["experience"] = f"{experience_list[0]} {experience_list[1]}"
        return job

    def _arranged_data(self, job: dict) -> dict:
        new_job = {}
        new_job["technical_id"] = job.pop("technical_id")
        new_job["source"] = FRANCE_TRAVAIL_SOURCE
        new_job["contents"] = job
        return new_job

    def process_job(self, job: dict) -> dict:
        new_job = job
        # new_job = self._process_activity(new_job)
        new_job = self._process_place(new_job)
        new_job = self._process_experience(new_job)
        new_job = self._process_salary(new_job)
        new_job = self._process_string(new_job)
        new_job = self._arranged_data(new_job)
        return new_job

    def process_file(self, dir: Path, source_file: Path) -> list:
        f = open(source_file)
        json_jobs_raw = json.load(f)["results"]
        json_jobs_cleaned = list(map(self.process_job, json_jobs_raw))
        f.close()
        self.write_jobs(json_jobs_cleaned, dir, source_file)
        return

    def _check_file(self, file: Path):
        return file.name.startswith(FRANCE_TRAVAIL_FILE_NAME + "_raw")


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
