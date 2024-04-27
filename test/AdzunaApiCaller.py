from helpers.HttpCaller import HttpCaller, UnauthorizedException
from helpers.Oauth2Helper import Oauth2Helper
import json
import datetime
import sys
from pathlib import Path

class AdzunaApiCaller:
    
    def __init__(self, api_id: str, api_key: str):
        self.api_id = api_id
        self.api_key = api_key
        self.jobs_search_url = f'https://api.adzuna.com/v1/api/jobs'


    def get_jobs_by_criterias(self, country, page, criteres: dict = {}) -> dict:

        headers = {
            "Accept": "application/json"
        }
        
        url = f'{self.jobs_search_url}/{country}/search/{page}'

        criteres['app_id'] = self.api_id
        criteres['app_key'] = self.api_key

        response = HttpCaller.get(url=url, headers=headers, params=criteres)

        if (response.status_code == 401 or response.status_code == 400): # if Unauthorized response, raise exception
            raise UnauthorizedException(response.message)
        
        return json.loads(response.text)
