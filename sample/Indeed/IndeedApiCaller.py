from helpers.HttpCaller import HttpCaller
import json

class IndeedApiCaller:
    ### Class for calling the Indeed APIs via Rapid API
    
    def __init__(self, job_search_url, job_details_url, rapid_api_key, rapid_api_host):
        self.jobs_search_url = job_search_url
        self.job_details_url = job_details_url
        self.rapid_api_key = rapid_api_key
        self.rapid_api_host = rapid_api_host
    
    def get_jobs_by_criterias(self, query, locality=""):
        ### Function to get jobs list by criterias
        ### Documentation here :
        # - https://rapidapi.com/mantiks-mantiks-default/api/indeed12/
    
        headers = {
            "X-RapidAPI-Key": self.rapid_api_key,
	        "X-RapidAPI-Host": self.rapid_api_host
        }
    
        params = {"query": query, "locality": locality}
    
        response = HttpCaller.get(self.jobs_search_url, headers, params)
        # Convert response to a JSON object
        jsonResponse = json.loads(response.text)
        
        return jsonResponse

    def get_job_details(self, job_id):
        ### Function to get jobs list by criterias
        ### Documentation here :
        # - https://rapidapi.com/mantiks-mantiks-default/api/indeed12/
    
        headers = {
            "X-RapidAPI-Key": self.rapid_api_key,
	        "X-RapidAPI-Host": self.rapid_api_host
        }
    
        url_for_job = self.job_details_url + "/" + job_id
    
        response = HttpCaller.get(url_for_job, headers)
        # Convert response to a JSON object
        jsonResponse = json.loads(response.text)
        
        return jsonResponse
