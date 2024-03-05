import yaml
import os
from FranceEmploi.FranceEmploiApiCaller import FranceEmploiApiCaller
from Indeed.IndeedApiCaller import IndeedApiCaller
from Muse.muse_data_extraction import Muse
import pandas as pd
import json



current_path = os.path.split(os.path.realpath(__file__))[0]

# Load credentials of API providers
with open(current_path + "/api_providers_credentials.yml", "r") as ymlfile:
    credentials = yaml.safe_load(ymlfile)
france_emploi_client_id = credentials["france_emploi"]["client_id"]
france_emploi_client_secret = credentials["france_emploi"]["client_secret"]
indeed_job_search_url = credentials["rapid_api"]["indeed"]["job_search_url"]
indeed_job_details_url = credentials["rapid_api"]["indeed"]["job_details_url"]
indeed_key = credentials["rapid_api"]["indeed"]["key"]
indeed_host = credentials["rapid_api"]["indeed"]["host"]

# Initialize the France Emploi API caller
franceEmploi = FranceEmploiApiCaller(france_emploi_client_id, france_emploi_client_secret)

# Authenticate to the France Emploi API services
franceEmploi.authenticate("api_offresdemploiv2 o2dsoffre", {"realm": "/partenaire"})

# Gets the jobs list with the criteria (=filter) on 'departement' with value '30'
franceEmploiJobs = franceEmploi.get_jobs_by_criterias({"departement":"30"})

# Showing the first job from the obtained list
print("Premier emploi depuis France Emploi: ", franceEmploiJobs['resultats'][0])



# Initialize the Indeed API caller
indeed = IndeedApiCaller(indeed_job_search_url, indeed_job_details_url, indeed_key, indeed_host)

# Gets the jobs list with the criteria (=filter) on query 'web developer' and locality 'fr' for France
indeedJobs = indeed.get_jobs_by_criterias("web developer", "fr")
firstIndeedJob = indeedJobs['hits'][0] 
print("Premier emploi depuis Indeed: ", firstIndeedJob)
firstIndeedJobDetails = indeed.get_job_details(firstIndeedJob['id'])
print("Détails du premier emploi depuis Indeed: ", firstIndeedJobDetails)

muse = Muse()
list_all_jobs_parsed = list()
for p in range(10):
    params = {"page": {p}, "descending": "true"}
    jobs_page = muse.get_jobs_by_criterias(params)
    jobs_parsed_list = muse.parse_job_from_page(jobs_page['results'])
    list_all_jobs_parsed = list_all_jobs_parsed + jobs_parsed_list

# write output as exemple
with open(f"{current_path}/Muse/muse_data_extraction.txt", 'w') as f:
    json.dump(list_all_jobs_parsed, f, indent=4)

df_all_jobs_parsed = pd.DataFrame(list_all_jobs_parsed)
df_all_jobs_parsed.to_csv(f"{current_path}/Muse/muse_data_extraction.csv")

print("treatment's over")
