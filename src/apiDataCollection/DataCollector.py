from apiDataCollection.apiCallers.FranceEmploiApiCaller import FranceEmploiApiCaller
from apiDataCollection.apiCallers.MuseApiCaller import MuseApiCaller
from apiDataCollection.apiCallers.AdzunaApiCaller import AdzunaApiCaller
from apiDataCollection.scraper.ApecScraper import ApecScraper
import requests
import pandas as pd
import os


class DataCollector:
    # Class for collecting the data from their sources

    france_emploi_client_id = ""
    france_emploi_client_secret = ""
    muse_client_secret = ""
    adzuna_api_id = ""
    adzuna_api_key = ""
    
    def __init__(self):
        pass

    @staticmethod
    def collectCredentialFromEnvVars():
        DataCollector.france_emploi_client_id = os.environ.get("FRANCE_EMPLOI_CLIENT_ID", "")
        DataCollector.france_emploi_client_secret = os.environ.get(
            "FRANCE_EMPLOI_CLIENT_SECRET", "")
        DataCollector.muse_client_secret = os.environ.get("MUSE_CLIENT_SECRET", "")
        DataCollector.adzuna_api_id = os.environ.get("ADZUNA_API_ID", "")
        DataCollector.adzuna_api_key = os.environ.get("ADZUNA_API_KEY", "")

        if DataCollector.france_emploi_client_id == "":
            raise CredentialNotFoundException(
                "FRANCE_EMPLOI_CLIENT_ID environment variable not found")
        if DataCollector.france_emploi_client_secret == "":
            raise CredentialNotFoundException(
                "FRANCE_EMPLOI_CLIENT_SECRET environment variable not found")
        if DataCollector.muse_client_secret == "":
            raise CredentialNotFoundException(
                "MUSE_CLIENT_SECRET environment variable not found")
        if DataCollector.adzuna_api_id == "":
            raise CredentialNotFoundException("ADZUNA_API_ID environment variable not found")
        if DataCollector.adzuna_api_key == "":
            raise CredentialNotFoundException("ADZUNA_API_KEY environment variable not found")

    @staticmethod
    def collect():
        print("Start of the step data collection")

        #DataCollector.__collectFromFranceEmploi()
        #DataCollector.__collectFromMuse()
        #DataCollector.__collectFromAdzuna()
        DataCollector.__collectFromApec()
        
        print("End of the step data collection")
        
    @staticmethod
    def __collectFromFranceEmploi():
        print("Start of data collection for France Emploi")
        # Initialize the France Emploi API caller
        franceEmploi = FranceEmploiApiCaller(DataCollector.france_emploi_client_id, \
            DataCollector.france_emploi_client_secret)

        # Authenticate to the France Emploi API services
        franceEmploi.authenticate("api_offresdemploiv2 o2dsoffre", {"realm": "/partenaire"})

        # Gets the jobs list with the criteria (=filter) on 'departement' with value '30'
        franceEmploiJobs = franceEmploi.get_jobs_by_criterias(
            {"departement": "30"})

        # Showing the first job from the obtained list
        print("Premier emploi depuis France Emploi: ",
              franceEmploiJobs['resultats'][0])

        print("End of data collection for France Emploi")

    @staticmethod
    def __collectFromMuse():
        print("Start of data collection for Muse")

        # Initialize the Muse API caller
        muse = MuseApiCaller(DataCollector.muse_client_secret)

        # Gets the jobs list with the criteria (=filter)
        list_all_jobs_parsed = list()
        for p in range(10):
            params = {"page": {p}, "descending": "true"}
            jobs_page = muse.get_jobs_by_criterias(params)
            jobs_parsed_list = muse.parse_job_from_page(jobs_page['results'])
            list_all_jobs_parsed = list_all_jobs_parsed + jobs_parsed_list

        print("End of data collection for Muse")

    @staticmethod
    def __collectFromAdzuna():
        Adzuna = AdzunaApiCaller(DataCollector.adzuna_api_id, \
            DataCollector.adzuna_api_key)
        
        country = 'fr'
        page = 1
        critere = {
            'results_per_page': '50',
            'sort_by': 'date',
            'max_days_old': '1',
        }

        adzuna_jobs = Adzuna.get_jobs_by_criterias(country=country, page=page, criteres=critere)
        print(adzuna_jobs)
        #    suite job
        # r = requests.get(f'https://api.adzuna.com/v1/api/jobs/fr/search/1', params=query)
        # response = r.json()
        # nb_count = response['count']
        # nb_page = ceil(nb_count/50)

        # keys_value = set()
            
        # start_time = time.time()
        # all_jobs = []
        # for page in range(1,2000):
        #     print(page)
        #     r = requests.get(f'http://api.adzuna.com/v1/api/jobs/fr/search/{page}', params=query)
        #     response = r.json()
        #     all_jobs.extend(response['results'])

        #     with open('all_jobs_22mars.json', 'w') as f:
        #         json.dump(all_jobs, f)
        
        #     df = pd.DataFrame(all_jobs)
        #     df.to_csv("all_jobs_22mars.csv")
                  
        # print(len(all_jobs))

        # with open('all_jobs.json', 'w') as f:
        #     json.dump(all_jobs, f)
        
        # df = pd.DataFrame(all_jobs)
        # df.to_csv("all_jobs.csv")
        
        # print("Start of the step data collection")

        # ['__CLASS__', 'adref', 'category', 'company', 'contract_time', 'contract_type', 'created', 'description', 'id', 'latitude', 'location', 'longitude', 'redirect_url', 'salary_is_predicted', 'salary_max', 'salary_min', 'title']

        # query = {'app_id': adzuna_client_id,
        #     'app_key': adzuna_client_secret,
        #     'content-type': 'application/json',
        #     'results_per_page': '50', # max 50
        #     'sort_by': 'date',
        #     'max_days_old': '1',
        # }
 
    @staticmethod
    def __collectFromApec():
        print("Start of data collection for Apec")

        # Initialize the Apec scraper
        apec = ApecScraper()

        # Gets the jobs list with the criteria (=filter)
        all_jobs_parsed = dict()
        for p in range(1, 300):
            print("Scraping of the page " + str(p))
            params = {"page": p, "descending": "true", "lieux": "799", "sortsType": "DATE"}
            jobs_parsed_list = apec.get_jobs_by_criterias(params)
            #print(jobs_parsed_list)
            # TODO Trouver comment ajouter le contenu du dict 'jobs_parsed_list' dans le dict 'all_jobs_parsed'
            # dict(all_jobs_parsed.items() | jobs_parsed_list.items())

        apec.close_scraper()
        
        #print(all_jobs_parsed)
        print("End of data collection for Apec")
        
class CredentialNotFoundException(Exception):
    pass
