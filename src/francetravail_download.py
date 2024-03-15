import yaml
from pathlib import Path
from FranceEmploi.FranceEmploiApiCaller \
    import FranceEmploiApiCaller, DepartmentJobsCaller


# Load credentials of API providers
with open(Path("./api_providers_credentials.yml"), "r") as ymlfile:
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

directory = "/home/celestine/smart_emploi_api/downloads/FranceTravail_15_03_2024"
Path(directory).mkdir(parents=True, exist_ok=True)
int_departments = list(range(1, 96, 1))
# int_departments.remove(20)
departments = [(f"{number:02d}") for number in int_departments]
departments += ["971", "972", "973", "974", "976"]
for dep in departments:
    departement_download = DepartmentJobsCaller(
        franceEmploi,
        path=directory,
        departement=dep,
        publieeDepuis=7)
    departement_download.get_jobs_by_department()
