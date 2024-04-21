from helpers.HttpCaller import HttpCaller, UnauthorizedException
import json


class MuseApiCaller:
    # Class for calling The Muse APIs with secret key
    # Documentation here :
    # - APIs catalog : https://www.themuse.com/developers/api/v2

    def __init__(self, client_secret: str):
        self.client_secret = client_secret
        self.jobs_search_url = "https://www.themuse.com/api/public/jobs"

    def get_jobs_by_criterias(self, criteres: dict = {}) -> dict:
        # Function to get jobs list by criterias
        # Documentation here :
        # - https://francetravail.io/data/api/offres-emploi?tabgroup-api=documentation
        # - https://francetravail.io/data/api/offres-emploi/documentation#/api-reference/operations/recupererListeOffre
        #
        # API parameters details :
        # url_job = "https://www.themuse.com/api/public/jobs"
        # location = "Abbeville%2C%20France"
        # page="1"
        # descending="true"
        # complete_url = f'{url_job}?location={location}&page={page}&descending={descending}'
        #
        # Examples :
        # # https://www.themuse.com/api/public/companies/15000161
        # https://www.themuse.com/api/public/companies?location=(.)*%2C%20France&page=1&descending=True
        # https://www.themuse.com/api/public/companies?location=Boston%2C%20MA&page=1&descending=True
        # https://www.themuse.com/api/public/companies?location=.*?%2C%20MA&page=1&descending=True

        body = {
            "api_key": self.client_secret,
        }

        response = HttpCaller.get(
            url=self.jobs_search_url, params=criteres, body=body)

        # if Unauthorized response, raise exception
        if (response.status_code == 401 or response.status_code == 400):
            raise UnauthorizedException(response.message)

        return json.loads(response.text)

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
