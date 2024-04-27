import requests
import logging

# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

fast_api_uri = f"http://127.0.0.1:8000/jobmarket"

# Fonction d'appel de l'API d'obtention du top XX des villes qui proposent le plus d'offres pour un département donné
def get_top_cities_for_dep(selected_department: str):
    return get(f"{fast_api_uri}/department/{selected_department}/town", "top cities for dep")

# Fonction d'appel de l'API d'obtention du top 5 des catégories d'emplois qui proposent le plus d'offres pour un département donné
def get_top_categories_for_dep(selected_department: str):
    return get(f"{fast_api_uri}/department/{selected_department}/category", "top 5 categories for dep")

def get(url: str, get_type: str):
    try: 
        response = requests.get(url)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as errh: 
        logger.error(f"Unexpected status code occurred during the retrieval of {get_type}", errh.args[0])
        return None