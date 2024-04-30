import logging
from abc import ABC, abstractmethod
import tempfile
import os
from pathlib import Path
from helpers.APIConstants import FTConstants, ApecConstants
import json
from unidecode import unidecode
import re
from datetime import datetime

JSON_KEYS = FTConstants.JSON_KEYS.value
HOMOGENIZED_JOBS = FTConstants.HOMOGENIZED_JOBS.value
FRANCE_TRAVAIL_FILE_NAME = FTConstants.FRANCE_TRAVAIL_FILE_NAME.value
FRANCE_TRAVAIL_SOURCE = 0
APEC_FILE_NAME = ApecConstants.APEC_FILE_NAME.value
APEC_SOURCE = 1
logger = logging.getLogger(__name__)


class JobsProcess(ABC):

    @abstractmethod
    def process_job(self, job: dict) -> dict:
        """_summary_

        Args:
            job (dict): _description_
        """
        pass

    @abstractmethod
    def _check_file(self, json_file: Path) -> bool:
        pass

    def process_directory(self, dir: Path):
        logger.info(f"Process directory {dir}")
        json_files = list(dir.glob('**/*.json'))
        for json_file in json_files:
            if self._check_file(json_file):
                logger.info(f"process json_file : {json_file}")
                file_size = os.path.getsize(json_file)
                if (file_size == 0):
                    logger.warning(f"{json_file} : Empty file")
                else:
                    self.process_file(dir, json_file)
                # rm file
                json_file.unlink()
                logger.info(f"{json_file} : file removed")
        logger.info("All files are processed")

    def process_file(self, dir: Path, source_file: Path) -> list:
        f = open(source_file)
        logger.debug("----------------------------")
        logger.debug(f"source_file : {source_file}")
        logger.debug(f"f : {f}")
        json_jobs_raw = json.load(f)["results"]
        json_jobs_cleaned = list(map(self.process_job, json_jobs_raw))
        f.close()
        self.write_jobs(json_jobs_cleaned, dir, source_file)
        return

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


class FTJobsProcess(JobsProcess):

    def __init__(self) -> None:
        pass

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
        logger.debug(job["place"]["libelle"])
        place = job["place"]["libelle"]
        dep_tmp = re.findall(r'\d+', place)
        # if dep
        if len(dep_tmp) > 0:
            dep = dep_tmp[0]
            place = place.replace(dep, "")
            if ('-' in place):
                town = (place.split('-', 1))[1]
            else:
                town = ""
        else:
            dep = ""
            town = place
        town = town.strip()
        dep = dep.strip()  # remove space
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
                logger.info("Job" + job["category"] +
                            " activity is not in the default list")
        return job

    def _process_salary(self, job: dict) -> dict:
        if "salary" in job:
            if "libelle" in job["salary"]:
                logger.debug(f"Process salary  + {job['salary']}")
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

    def _check_file(self, file: Path):
        return file.name.startswith(FRANCE_TRAVAIL_FILE_NAME + "_raw")


class ApecJobsProcess(JobsProcess):

    def __init__(self) -> None:
        pass

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
        # Example : Monaco, Lille - 59, Blabla - 997
        place = job["place"]
        # all digit values
        dep_tmp = re.findall(r'\d+', place)
        # if dep
        if len(dep_tmp) > 0:
            dep = dep_tmp[-1]
            place = place.replace(dep, "")
            town = (place.rsplit('-', 1))[0]
        else:
            dep = ""
            town = place
        town = town.strip()
        dep = dep.strip()  # remove space
        job["place"] = {"town": town,
                        "department": dep}
        return job

    def _process_date(self, job: dict) -> dict:
        job["publication_date"] = datetime.strptime(
            job["publication_date"][-10:], '%d/%m/%Y').isoformat() + ".000Z"
        job["actualisation_date"] = datetime.strptime(
            job["actualisation_date"][-10:], '%d/%m/%Y').isoformat() + ".000Z"
        return job

    def _arranged_data(self, job: dict) -> dict:
        new_job = {}
        new_job["technical_id"] = job.pop("technical_id")
        new_job["source"] = APEC_SOURCE
        new_job["contents"] = job
        return new_job

    def process_job(self, job: dict) -> dict:
        new_job = job
        new_job = self._process_place(new_job)
        # new_job = self._process_salary(new_job)
        new_job = self._process_string(new_job)
        new_job = self._process_date(new_job)
        new_job = self._arranged_data(new_job)
        return new_job

    def _check_file(self, file: Path):
        return file.name.startswith(APEC_FILE_NAME + "_raw")
