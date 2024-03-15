import yaml
import os
from FranceEmploi.FranceEmploiApiCaller \
    import FranceEmploiApiCaller, DepartmentJobsCaller

current_path = os.path.split(os.path.realpath(__file__))[0]
# Load credentials of API providers
with open(current_path + "/api_providers_credentials.yml", "r") as ymlfile:
    credentials = yaml.safe_load(ymlfile)
france_emploi_client_id = credentials["france_emploi"]["client_id"]
france_emploi_client_secret = credentials["france_emploi"]["client_secret"]

# Initialize the France Emploi API caller
franceEmploi = FranceEmploiApiCaller(
    france_emploi_client_id, france_emploi_client_secret)

# Authenticate to the France Emploi API services
franceEmploi.authenticate("api_offresdemploiv2 o2dsoffre", {
                          "realm": "/partenaire"})

response = franceEmploi.get_jobs_by_criterias({"departement": "30"})

print(response.headers)

departement_download = DepartmentJobsCaller(
    franceEmploi,
    path="/home/celestine/smart_emploi_api/downloads",
    departement="30")
departement_download.get_jobs_by_department()
