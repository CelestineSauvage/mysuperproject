from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from urllib import parse
import time

class ApecScraper:
    ### Class for scraping the Apec website
    
    def __init__(self):
        self.jobs_search_url = "https://www.apec.fr/candidat/recherche-emploi.html/emploi"
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    
    def get_jobs_by_criterias(self, criteres: dict = {}) -> dict:
        ### Function to get jobs list by criterias
        ### Documentation here : 
        #
        ### URL parameters details :
        # lieux = 799 (France)
        # sortsType = DATE (décroissant)
        # page = 1
        
        current_url = self.jobs_search_url + "?" + parse.urlencode(criteres)
        
        # open web page
        self.driver.get(current_url)
        
        # wait for element with class 'container-result' to be added
        container_result = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "container-result")))
        
        # scroll to container-result
        self.driver.execute_script("arguments[0].scrollIntoView();", container_result)
        
        all_divs_offer = self.driver.find_elements(By.XPATH, "//div[@class = 'card-offer__text']")
                
        parsed_jobs = []
        for div_offer in all_divs_offer:
            parsed_job = self.__parse_job_from_listing_page(div_offer)
            parsed_jobs.append(parsed_job)
        
        for parsed_job in parsed_jobs:
            parsed_job = self.__parse_job_from_detail_page(parsed_job)
        
        return parsed_jobs

    def __parse_job_from_listing_page(self, div_offer) -> dict :
        parsed_job = dict()
        parsed_job["source"] = 2 # Apec
        parsed_job["url"] = self.__try_to_find_attribute_value_of_element_by_xpath(div_offer, ".//ancestor::a[1]", "href", "")
        
        id_start_index = parsed_job["url"].index("/detail-offre/") + 14
        id_end_index = id_start_index + 10
        parsed_job["technical_id"] = parsed_job["url"][id_start_index:id_end_index]
        
        parsed_job["company"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//p[contains(@class, 'card-offer__company')]", parsed_job["technical_id"])
        parsed_job["title"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//h2[contains(@class, 'card-title')]", parsed_job["technical_id"])
        parsed_job["description"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//p[contains(@class, 'card-offer__description')]", parsed_job["technical_id"])
        parsed_job["salary"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer']/li[1]", parsed_job["technical_id"])
        parsed_job["contract_type"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[1]", parsed_job["technical_id"])
        parsed_job["place"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[2]", parsed_job["technical_id"])
        parsed_job["publication_date"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[@title = 'Date de publication']", parsed_job["technical_id"])
        
        return parsed_job

    def __parse_job_from_detail_page(self, parsed_job: dict) -> dict :
        # open web page
        self.driver.get(parsed_job["url"])
        
        # wait for element with name 'apec-detail-emploi' to be added
        driverElements = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'date-offre') and contains(text(), 'Publiée le')]")))
        
        description_in_p_tags = self.__try_to_find_elements_by_xpath(driverElements, "//div[@class='col-lg-8 border-L']/div[@class = 'details-post']/p", parsed_job["technical_id"])
        description = ""
        for p_tag in description_in_p_tags:
            description += p_tag.text + "\n"
        
        parsed_job["description"] = description
        parsed_job["publication_date"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[contains(@class, 'date-offre') and contains(text(), 'Publiée le')]", parsed_job["technical_id"])
        parsed_job["actualisation_date"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[contains(@class, 'date-offre') and contains(text(), 'Actualisée le')]", parsed_job["technical_id"])
        parsed_job["sector"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[@class = 'details-post']/h4[contains(text(), 'Secteur d')]/parent::div/span", parsed_job["technical_id"])
        parsed_job["experience"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[@class = 'details-post']/h4[text() = 'Expérience']/parent::div/span", parsed_job["technical_id"])
        parsed_job["contract_time"] = None
        parsed_job["competences"] = None

        return parsed_job
    
    def __try_to_find_text_of_element_by_xpath(self, driverElements, xpath: str, technical_id) -> str :
        try:
            return driverElements.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            print("Exception handled on element with APEC ID = " + technical_id + " searching by this XPATH :" + xpath)
            return ""
    
    def __try_to_find_elements_by_xpath(self, driverElements, xpath: str, technical_id):
        try:
            return driverElements.find_elements(By.XPATH, xpath)
        except NoSuchElementException:
            print("Exception handled on element with APEC ID = " + technical_id + "searching by this XPATH :" + xpath)
            return ""

    def __try_to_find_attribute_value_of_element_by_xpath(self, driverElements, xpath: str, attributeName: str, technical_id) -> str :
        try:
            return driverElements.find_element(By.XPATH, xpath).get_attribute(attributeName)
        except NoSuchElementException:
            print("Exception handled on element with APEC ID = " + technical_id + "searching by this XPATH :" + xpath)
            return ""
    
    def close_scraper(self):
        # quit webdriver
        self.driver.quit()