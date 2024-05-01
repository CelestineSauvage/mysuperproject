import requests
import logging

# setup logger
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

fast_api_uri = f"http://127.0.0.1:8000/jobmarket"

# Fonction d'appel de l'API d'obtention de la liste des départements
def get_departments():
    return get(f"{fast_api_uri}/departments", "Departments list")

# Fonction d'appel de l'API d'obtention du top XX des villes qui proposent le plus d'offres pour un département donné
def get_top_cities_for_dep(selected_department: str):
    return get(f"{fast_api_uri}/department/{selected_department}/town", "top cities for dep")

# Fonction d'appel de l'API d'obtention du top 5 des catégories d'emplois qui proposent le plus d'offres pour un département donné
def get_top_categories_for_dep(selected_department: str):
    return get(f"{fast_api_uri}/department/{selected_department}/category", "top 5 categories for dep")

# Fonction d'appel de l'API d'obtention de la répartition des offres d'emploi selon le niveau d'expérience pour un département donné
def get_job_repartition_by_experience_level_for_dep(selected_department: str):
    return get(f"{fast_api_uri}/department/{selected_department}/experience", "job repartition by experience level for dep")

# Fonction d'appel de l'API d'obtention de la répartition des offres d'emploi selon le type de contrat pour un département donné
def get_job_repartition_by_contract_type_for_dep(selected_department: str):
    return get(f"{fast_api_uri}/department/{selected_department}/contract", "job repartition by contract type for dep")

# Fonction d'appel de l'API d'obtention du nombre de jobs pour un département avec recherche par texte libre
def get_job_number_for_dep_on_search(selected_department: str, search_text: str):
    return get(f"{fast_api_uri}/department/{selected_department}/contract", "job number for department on search text", {"search" : search_text})

def get(url: str, get_type: str, params: dict = None):
    try: 
        response = requests.get(url, params = params)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as errh: 
        logger.error(f"Unexpected status code occurred during the retrieval of {get_type}", errh.args[0])
        return None