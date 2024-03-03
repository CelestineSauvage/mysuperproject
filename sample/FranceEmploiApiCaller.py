from helpers.HttpCaller import HttpCaller
import json

class FranceEmploiApiCaller:
    ### Class for calling the France Emploi APIs with OAth2 authentication
    ### Documentation here : 
    # - Workflow to follow to use the France Travail Connect APIs : https://francetravail.io/data/documentation/comprendre-dispositif-pole-emploi-connect/open-id-connect
    # - APIs catalog : https://francetravail.io/data/api
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_access_token(self, scope, params = ''):
        ### Function to get an access token via the 'client_credentials' OAuth2 Grant Type
        # Documentation here :  
        # - https://francetravail.io/data/documentation/utilisation-api-pole-emploi/generer-access-token
        # - https://www.oauth.com/oauth2-servers/access-tokens/client-credentials/

        url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token"

        content_type = "application/x-www-form-urlencoded"
        
        body = {
            "grant_type": "client_credentials", 
            "client_id": self.client_id, 
            "client_secret": self.client_secret, 
            "scope": scope,
        }

        response = HttpCaller.post(url, content_type, params, body)
        # Convert response to a JSON object
        jsonResponse = json.loads(response.text)
        access_token = jsonResponse["access_token"]
        expire = jsonResponse["expires_in"]
        print("Obtained access_token", access_token, "that expires in", expire / 60, "minutes.")
        
        return access_token


    def get_offres_demploi_par_criteres(self, access_token, criteres={}): #, criteres
        ### Function to get an access token via the 'client_credentials' OAuth2 Grant Type
        ### Documentation here : 
        ### - https://francetravail.io/data/api/offres-emploi?tabgroup-api=documentation
        ### - https://francetravail.io/data/api/offres-emploi/documentation#/api-reference/operations/recupererListeOffre
        
        url = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
    
        response = HttpCaller.get(url, access_token, criteres)
        # Convert response to a JSON object
        jsonResponse = json.loads(response.text)
        
        return jsonResponse
