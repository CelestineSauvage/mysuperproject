import requests

class HttpCaller:
    ### Class for calling HTTP APIs with OAth2 authentication
    
    def __init__(self):
        pass

    @staticmethod
    def get(url, header_params={}, params={}):
        ### Static function to execute a GET query with OAuth2 authentication
        
        # Get the results    
        response = requests.get(
            url,
            headers = header_params,
            params = params
        )
        
        HttpCaller.__print_status_code(url, response)
        return response

    @staticmethod
    def post(url, header_params={}, params={}, body={}):
        ### Static function to execute a POST query with OAuth2 authentication
        
        # Get the access token
        response = requests.post(
            url,
            data = body,
            headers = header_params,
            params = params,
        )
        
        HttpCaller.__print_status_code(url, response)
        return response
    
    @classmethod
    def __print_status_code(self, url, response):
        print("Status Code for HTTP POST on", url, ':', response.status_code)

class UnauthorizedException(Exception):
    pass