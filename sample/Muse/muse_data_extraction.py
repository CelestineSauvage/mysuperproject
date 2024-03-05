from helpers.HttpCaller import HttpCaller
# from dateutil.parser import parse
import json


class Muse:
    def __init__(self):
        self.main_url = "https://www.themuse.com/api/public"
        # self.companies = []
        # self.jobs = []

    def get_jobs_by_criterias(self, criteres={}):
        response = HttpCaller.get(f'{self.main_url}/jobs', header_params=None, params=criteres)
        json_response = json.loads(response.text)

        return json_response

    def parse_job_from_page(self, jobs):
        parsed_jobs = []
        for job in jobs:
            job_parsed = self.get_job_info(job)
            parsed_jobs.append(job_parsed)
        return parsed_jobs

    def get_job_info(self, job):
        output = dict()
        output["technical_id"] = job["id"]
        output["fonctionnal_name"] = job["short_name"]
        output["name"] = job["name"]
        output["description"] = job["contents"]
        output["place"] = job["locations"]
        # output["publication_date"] = parse(job["publication_date"])
        output["publication_date"] = job["publication_date"]
        output["qualification_level"] = None
        if len(job["categories"]) > 0:
            output["category"] = job["categories"][0]["name"]
        else:
            output["category"] = None
        output["level"] = job["levels"][0]["short_name"]
        output["type"] = job["type"]
        output["salary"] = None
        output["link"] = job["refs"]['landing_page']
        return output

# location
# url_job = "https://www.themuse.com/api/public/jobs"
# location = "Abbeville%2C%20France"
# page="1"
# descending="true"
# complete_url = f'{url_job}?location={location}&page={page}&descending={descending}'

# Companies
# # https://www.themuse.com/api/public/companies/15000161
# https://www.themuse.com/api/public/companies?location=(.)*%2C%20France&page=1&descending=True
# https://www.themuse.com/api/public/companies?location=Boston%2C%20MA&page=1&descending=True
# https://www.themuse.com/api/public/companies?location=.*?%2C%20MA&page=1&descending=True
