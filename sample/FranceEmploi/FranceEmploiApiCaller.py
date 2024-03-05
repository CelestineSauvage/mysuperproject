from helpers.HttpCaller import HttpCaller
from helpers.Oauth2Helper import Oauth2Helper
import json

class FranceEmploiApiCaller:
    ### Class for calling the France Emploi APIs with OAth2 authentication
    ### Documentation here : 
    # - Workflow to follow to use the France Travail Connect APIs : https://francetravail.io/data/documentation/comprendre-dispositif-pole-emploi-connect/open-id-connect
    # - APIs catalog : https://francetravail.io/data/api
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token"
        self.jobs_search_url = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
        self.access_token = ""
    
    def authenticate(self, scope: str, params: dict = {}):
        ### Function to get an access token via OAuth2 Grant Type
        # Documentation here :  
        # - https://francetravail.io/data/documentation/utilisation-api-pole-emploi/generer-access-token
        self.access_token = Oauth2Helper.get_access_token_by_client_credential(
            access_token_url = self.access_token_url, scope = scope, client_id = self.client_id,
            client_secret = self.client_secret, params = params
        )

    def get_jobs_by_criterias(self, criteres: dict = {}) -> dict:
        ### Function to get jobs list by criterias
        ### Documentation here : 
        # - https://francetravail.io/data/api/offres-emploi?tabgroup-api=documentation
        # - https://francetravail.io/data/api/offres-emploi/documentation#/api-reference/operations/recupererListeOffre
    
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json"
        }
    
        response = HttpCaller.get(url = self.jobs_search_url, headers = headers, params = criteres)
        # Convert response to a JSON object
        jsonResponse = json.loads(response.text)
        
        return jsonResponse
