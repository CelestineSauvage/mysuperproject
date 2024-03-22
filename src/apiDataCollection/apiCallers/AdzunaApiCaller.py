from helpers.HttpCaller import HttpCaller, UnauthorizedException
from helpers.Oauth2Helper import Oauth2Helper
import json
import datetime 
import sys
from pathlib import Path

class AdzunaApiCaller:
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.jobs_search_url = f'https://api.adzuna.com/v1/api/jobs'


    def get_jobs_by_criterias(self, country, page, criteres: dict = {}) -> dict:

        headers = {
            "Accept": "application/json"
        }
        
        url = f'{self.jobs_search_url}/{country}/search/{page}'

        criteres['app_id'] = self.client_id
        criteres['app_key'] = self.client_secret

        response = HttpCaller.get(url=url, headers=headers, params=criteres)

        if (response.status_code == 401 or response.status_code == 400): # if Unauthorized response, raise exception
            raise UnauthorizedException(response.message)
        
        return response