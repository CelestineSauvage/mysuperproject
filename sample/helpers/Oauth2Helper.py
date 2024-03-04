import json
from helpers.HttpCaller import HttpCaller

class Oauth2Helper:
    ### Class for OAuth2 authentication
    
    def __init__(self):
        pass

    @staticmethod
    def get_access_token_by_client_credential(access_token_url, scope, client_id, client_secret, params = ''):
        ### Function to get an access token via the 'client_credentials' OAuth2 Grant Type
        # - https://www.oauth.com/oauth2-servers/access-tokens/client-credentials/

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        body = {
            "grant_type": "client_credentials", 
            "client_id": client_id, 
            "client_secret": client_secret, 
            "scope": scope,
        }

        response = HttpCaller.post(access_token_url, headers, params, body)
        
        # Convert response to a JSON object
        jsonResponse = json.loads(response.text)
        access_token = jsonResponse["access_token"]
        expire = int(jsonResponse["expires_in"])
        print("Obtained access_token", access_token, "that will expires in", expire / 60, "minutes.")
        
        return access_token
