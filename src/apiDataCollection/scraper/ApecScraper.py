import logging
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from urllib import parse
from retry import retry
from apiDataCollection.APIConstants import ApecConstants
from helpers.Chronometer import Chronometer
from datetime import datetime
from pathlib import Path
import json

JSON_FILE_NAME = ApecConstants.APEC_FILE_NAME.value
ACCEPTED_CRITERAS = ApecConstants.ACCEPTED_CRITERAS.value
logger = logging.getLogger(__name__)

class ApecScraper:
    ### Class for scraping the Apec website
    
    chrono = Chronometer()
    
    def __init__(self, dir_path: Path):
        self.jobs_search_url = "https://www.apec.fr/candidat/recherche-emploi.html/emploi"
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.dir_path = dir_path

    @chrono.timeit
    def get_jobs_by_criterias(self, criteres: dict = {}):
        """get jobs by specified criterias

        Args:
            criteres (dict, optional): list of criterias. Defaults to {}.

        Raises:
            UnauthorizedException: exit if HTTP response is 400 or 401

        Returns:
            dict: jobs
        """
        
        assert (
            key in ACCEPTED_CRITERAS for key in criteres.keys())
        
        total_results = self.__get_total_jobs_from_listing_page(self.jobs_search_url + "?" + parse.urlencode(criteres))
        
        total_pages = total_results // 20 # to round by excess (in order to be sure to get the last page in any case)
        
        criteres["page"] = 1
        
        logger.info(f"Expected scraping of {total_pages} page(s)")
        
        for page in range(1, total_pages + 1, 1):
            self.__process_page(page, total_pages, criteres)

    @chrono.timeit
    def __process_page(self, page: int, total_pages, criteres):
        logger.info(f"Scraping of page {page} on {total_pages}")
            
        criteres["page"] = page   
        current_url = self.jobs_search_url + "?" + parse.urlencode(criteres)
        
        try:
            all_divs_offer = self.__get_jobs_from_listing_page(current_url, page)
                
            parsed_jobs = []
            for div_offer in all_divs_offer:
                parsed_job = self.__parse_job_from_listing_page(div_offer)
                parsed_jobs.append(parsed_job)
            
            for parsed_job in parsed_jobs:
                parsed_job = self.__parse_job_from_details_page(parsed_job, str(criteres["page"]))
            
            results = {}
            results["results"]  = parsed_jobs
            self.__save_json_file(page, results)
            logger.info(f"Page {page} successfully scraped with {len(parsed_jobs)} element(s) and saved to a JSON file")
        except NoSuchElementException:
            logger.error(f"Page {page} defeated scraped")
            pass
        except TimeoutException:
            logger.error(f"Page {page} defeated scraped")
            pass
    
    def __save_json_file(self, page: int, json_data):
        current_dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"{JSON_FILE_NAME}_page{page}_{current_dt}" + ".json"
        full_file_name = self.dir_path / Path(file_name)
        
        with open(full_file_name, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

    @retry((WebDriverException), tries=3, delay=1)
    def __open_web_page(self, url: str):
        self.driver.get(url)

    @retry((TimeoutException, NoSuchElementException, StaleElementReferenceException), tries=3, delay=1)
    def __get_total_jobs_from_listing_page(self, url: str) -> int:
        self.__open_web_page(url)
        
        xpath_total_pages = "//div[@class = 'number-candidat']/span"
        
        # wait for element with class 'container-result' to be added
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, xpath_total_pages)))
        except TimeoutException as ex:
            logger.error(f"TimeoutException has been thrown for __get_total_pages_from_listing_page() on URL {url}")
            raise ex
    
        try:
            return int(self.driver.find_element(By.XPATH, xpath_total_pages).text.replace(" ", ""))
        except NoSuchElementException:
            logger.error(f"NoSuchElementException handled on element total pages searching by this XPATH : {xpath_total_pages}")
            raise ex
        except StaleElementReferenceException:
            logger.error(f"StaleElementReferenceException handled on element total pages searching by this XPATH : {xpath_total_pages}")
            raise ex
    
    @retry((TimeoutException, NoSuchElementException, StaleElementReferenceException), tries=3, delay=1)
    def __get_jobs_from_listing_page(self, current_url : str, page : int) -> dict :
        self.__open_web_page(current_url)
        
        # wait for element with class 'container-result' to be added
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'container-result']")))
        except TimeoutException as ex:
            logger.error(f"TimeoutException has been thrown for get_jobs_by_criterias() on page {page}")
            raise ex
        
        xpath_total_pages = "//div[@class = 'card-offer__text']"
        
        try:
            return self.driver.find_elements(By.XPATH, xpath_total_pages)
        except NoSuchElementException:
            logger.error(f"NoSuchElementException handled on container-result of a listing page by searching by this XPATH : {xpath_total_pages}")
            raise ex
        except StaleElementReferenceException:
            logger.error(f"StaleElementReferenceException handled on container-result of a listing page by searching by this XPATH : {xpath_total_pages}")
            raise ex
    
    def __parse_job_from_listing_page(self, div_offer) -> dict :
        parsed_job = {}
        
        url = self.__try_to_find_attribute_value_of_element_by_xpath(div_offer, ".//ancestor::a[1]", "href", "")
        
        parsed_job["url"] = url
        
        id_start_index = url.index("/detail-offre/") + 14
        id_end_index = id_start_index + 10
        technical_id = url[id_start_index:id_end_index]
        
        parsed_job["technical_id"] = technical_id
        parsed_job["place"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[2]", technical_id)
        parsed_job["publication_date"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[@title = 'Date de publication']", technical_id)
        parsed_job["actualisation_date"] = None
        parsed_job["category"] = None
        parsed_job["title"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//h2[contains(@class, 'card-title')]", technical_id)
        parsed_job["contract_type"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[1]", technical_id)
        parsed_job["experience"] = None
        parsed_job["salary"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer']/li[1]", technical_id)
        parsed_job["description"] = None
        #parsed_job["company"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//p[contains(@class, 'card-offer__company')]", technical_id)
        
        return parsed_job

    @retry((TimeoutException, NoSuchElementException), tries=3, delay=1)
    def __parse_job_from_details_page(self, parsed_job: dict, page: int) -> dict :
        technical_id = parsed_job["technical_id"]
        logger.info(f"Scraping details of job {technical_id} for page {page}")
        
        self.__open_web_page(parsed_job["url"])
        
        # wait for element with name 'apec-detail-emploi' to be added        
        try:
            driverElements = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'date-offre') and contains(text(), 'Publiée le')]")))
        except TimeoutException as ex:
            logger.error(f"TimeoutException has been thrown for __parse_job_from_details_page() on job with ID {technical_id}")
            raise ex
        
        if driverElements == None:
            logger.error(f"NoSuchElementException has been thrown for __parse_job_from_details_page() on job with ID {technical_id}")
            raise NoSuchElementException()
        
        description = ""
        description_in_p_tags = self.__try_to_find_elements_by_xpath(driverElements, "//div[@class='col-lg-8 border-L']/div[@class = 'details-post']/p", technical_id)
        if len(description_in_p_tags) > 0:
            for p_tag in description_in_p_tags:
                description += p_tag.text
            
        parsed_job["description"] = description
        parsed_job["publication_date"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[contains(@class, 'date-offre') and contains(text(), 'Publiée le')]", technical_id)
        parsed_job["actualisation_date"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[contains(@class, 'date-offre') and contains(text(), 'Actualisée le')]", technical_id)
        parsed_job["category"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[@class = 'details-post']/h4[contains(text(), 'Secteur d')]/parent::div/span", technical_id)
        parsed_job["experience"] = self.__try_to_find_text_of_element_by_xpath(driverElements, "//div[@class = 'details-post']/h4[text() = 'Expérience']/parent::div/span", technical_id)

        parsed_job.pop("url") # Not needed anymore
        
        return parsed_job
        
    def __try_to_find_text_of_element_by_xpath(self, driverElements, xpath: str, technical_id: str) -> str :
        try:
            return driverElements.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            logger.error(f"Exception handled on element on job with ID {technical_id} searching by this XPATH : {xpath}")
            return ""
    
    def __try_to_find_elements_by_xpath(self, driverElements, xpath: str, technical_id: str):
        try:
            return driverElements.find_elements(By.XPATH, xpath)
        except NoSuchElementException:
            logger.error(f"Exception handled on element on job with ID {technical_id} searching by this XPATH : {xpath}")
            return ""

    def __try_to_find_attribute_value_of_element_by_xpath(self, driverElements, xpath: str, attributeName: str, technical_id: str) -> str :
        try:
            return driverElements.find_element(By.XPATH, xpath).get_attribute(attributeName)
        except NoSuchElementException:
            logger.error(f"Exception handled on element on job with ID {technical_id} searching by this XPATH : {xpath}")
            return ""
    
    def close_scraper(self):
        # quit webdriver
        self.driver.quit()