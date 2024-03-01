import requests
   

def get_access_token(access_token_url, client_id, client_secret, scope, params = ''):
    ### Function to get an access token via the 'client_credentials' OAuth2 Grant Type
    ### Documentation here : https://www.oauth.com/oauth2-servers/access-tokens/client-credentials/
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    body = {
        "grant_type": "client_credentials", 
        "client_id": client_id, 
        "client_secret": client_secret, 
        "scope": scope,
    }
    
    # Get the access token
    response = requests.post(
        access_token_url,
        data = body,
        headers = headers,
        params = params,
    )
    
    print("Status Code for get_access_token() :", response.status_code)
    return response.json()['access_token']

def get(url, access_token, query_params={}):
    ### Function for a GET query with OAuth2
    
    bearer = "Bearer " + access_token
    
    headers = {
        "Authorization": bearer,
        "Accept": "application/json"
    }
    
    # Get the results    
    response = requests.get(
        url,
        headers = headers,
        params = query_params
    )
    
    print("Status Code for get() :", response.status_code)
    return response.json()


def get_offres_demploi_par_criteres(access_token): #, criteres
    ### Function to get an access token via the 'client_credentials' OAuth2 Grant Type
    ### Documentation here : 
    ### - https://francetravail.io/data/api/offres-emploi?tabgroup-api=documentation
    ### - https://francetravail.io/data/api/offres-emploi/documentation#/api-reference/operations/recupererListeOffre
    
    url = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
    
    return get(url, access_token, {"departement":"30"})
    


### DOCUMENTATION :
### Workflow to follow to use the France Travail Connect APIs : https://francetravail.io/data/documentation/comprendre-dispositif-pole-emploi-connect/open-id-connect
### France Travail Connect APIs catalog : https://francetravail.io/data/api

# Cf : https://francetravail.io/data/documentation/utilisation-api-pole-emploi/generer-access-token

access_token = get_access_token(
        "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token", 
        "PAR_francetravailpourproj_07af7086caa6684d7bfdeb93773ac2232bcab87c28126890c3dd2c3a7d41ae23", 
        "61bd84de5eacdf9e4654c8bd3e67faff2781e5a93fa9c1186baa274a2bf933d3",
        {"api_offresdemploiv2", "o2doffre"},
        {"realm": "/partenaire"}
    )
print("Obtained token :", access_token)

print("-------")
print("-------")

offres_emploi = get_offres_demploi_par_criteres(access_token)
print(offres_emploi)
