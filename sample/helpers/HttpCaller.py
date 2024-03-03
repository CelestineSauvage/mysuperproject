import requests

class HttpCaller:
    ### Class for calling HTTP APIs with OAth2 authentication
    
    def __init__(self):
        pass

    @staticmethod
    def get(url, access_token, params={}):
        ### Static function to execute a GET query with OAuth2 authentication
        
        bearer = "Bearer " + access_token
        
        headers = {
            "Authorization": bearer,
            "Accept": "application/json"
        }
        
        # Get the results    
        response = requests.get(
            url,
            headers = headers,
            params = params
        )
        
        HttpCaller.__print_status_code(url, response)
        return response

    @staticmethod
    def post(url, content_type, params={}, body={}):
        ### Static function to execute a POST query with OAuth2 authentication
        
        headers = {
            "Content-Type": content_type
        }
        
        # Get the access token
        response = requests.post(
            url,
            data = body,
            headers = headers,
            params = params,
        )
        
        HttpCaller.__print_status_code(url, response)
        return response
    
    @classmethod
    def __print_status_code(self, url, response):
        print("Status Code for HTTP POST on", url, ':', response.status_code)