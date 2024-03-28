from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from urllib import parse
from retry import retry
from apiDataCollection.scraper.ElementsNotFoundExceptionForDivsOffer import ElementsNotFoundExceptionForDivsOffer
from apiDataCollection.scraper.ElementsNotFoundExceptionForDriver import ElementsNotFoundExceptionForDriver
from apiDataCollection.scraper.TimeoutExceptionForDriverElements import TimeoutExceptionForDriverElements
from apiDataCollection.APIConstants import ApecConstants
from helpers.Chronometer import Chronometer
from json import dumps
from datetime import datetime

JSON_FILE_NAME = ApecConstants.APEC_FILE_NAME.value
ACCEPTED_CRITERAS = ApecConstants.ACCEPTED_CRITERAS.value

class ApecScraper:
    ### Class for scraping the Apec website
    
    chrono = Chronometer()
    
    def __init__(self):
        self.jobs_search_url = "https://www.apec.fr/candidat/recherche-emploi.html/emploi"
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    @chrono.timeit
    @retry((TimeoutException, ElementsNotFoundExceptionForDivsOffer), tries=3, delay=1)
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
        
        if total_results == None:
            return
        
        total_pages = total_results // 20 # to round by excess (in order to be sure to get the last page in any case)
        
        criteres["page"] = 1
        
        for page in range(1, total_pages, 1):
            print("Scraping of page " + str(page) + " on " + str(total_pages))
            
            criteres["page"] = page   
            current_url = self.jobs_search_url + "?" + parse.urlencode(criteres)
            
            try:
                # open web page
                self.driver.get(current_url)
                
                # wait for element with class 'container-result' to be added
                try:
                    WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'container-result']")))
                except TimeoutException as ex:
                    print("TimeoutException has been thrown for get_jobs_by_criterias() on page " + str(criteres["page"]))
                    raise ex
                
                all_divs_offer = self.driver.find_elements(By.XPATH, "//div[@class = 'card-offer__text']")
                
                if len(all_divs_offer) == 0:
                    print("ElementsNotFoundExceptionForDivsOffer has been thrown for get_jobs_by_criterias() on page " + str(criteres["page"]))
                    raise ElementsNotFoundExceptionForDivsOffer()    
                    
                parsed_jobs = []
                for div_offer in all_divs_offer:
                    parsed_job = self.__parse_job_from_listing_page(div_offer)
                    parsed_jobs.append(parsed_job)
                
                for parsed_job in parsed_jobs:
                    try:
                        parsed_job = self.__parse_job_from_details_page(parsed_job, str(criteres["page"]))
                    except TimeoutExceptionForDriverElements as ex:
                        raise ex
                
                results = {}
                results["results"] = parsed_jobs
                
                self.__save_json_file(page, results)
                print("=> Page " + str(page) + " successfully scraped with " + str(len(results["results"])) + " element(s) and saved to a JSON file")
            except TimeoutException:
                print("=> Page " + str(page) + " defeated scraped")
                pass
            except ElementsNotFoundExceptionForDivsOffer:
                print("=> Page " + str(page) + " defeated scraped")
                pass
            except ElementsNotFoundExceptionForDriver:
                print("=> Page " + str(page) + " defeated scraped")
                pass
            except TimeoutExceptionForDriverElements:
                print("=> Page " + str(page) + " defeated scraped")
                pass

    def __save_json_file(self, page: int, json_data):
        current_dt = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"{JSON_FILE_NAME}_page{page}_{current_dt}" + ".json"
        full_file_name = "jobs_result_apec/" + file_name
        print(full_file_name)
        with open(full_file_name, "w") as json_file:
            json_file.write(dumps(json_data))

    @retry((TimeoutException), tries=3, delay=1)
    def __get_total_jobs_from_listing_page(self, url: str) -> int:
        # open web page
        self.driver.get(url)
        
        xpath_total_pages = "//div[@class = 'number-candidat']/span"
        
        # wait for element with class 'container-result' to be added
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, xpath_total_pages)))
        except TimeoutException as ex:
            print("TimeoutException has been thrown for __get_total_pages_from_listing_page() on URL " + url)
            raise ex
    
        try:
            return int(self.driver.find_element(By.XPATH, xpath_total_pages).text.replace(" ", ""))
        except NoSuchElementException:
            print("Exception handled on element total pages searching by this XPATH :" + xpath_total_pages)
            return None
        
    def __parse_job_from_listing_page(self, div_offer) -> dict :
        parsed_job = {}
        parsed_job["source"] = 2 # Apec
        parsed_job["url"] = self.__try_to_find_attribute_value_of_element_by_xpath(div_offer, ".//ancestor::a[1]", "href", "")
        
        id_start_index = parsed_job["url"].index("/detail-offre/") + 14
        id_end_index = id_start_index + 10
        parsed_job["technical_id"] = parsed_job["url"][id_start_index:id_end_index]
        
        parsed_job["company"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//p[contains(@class, 'card-offer__company')]", parsed_job["technical_id"])
        parsed_job["title"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//h2[contains(@class, 'card-title')]", parsed_job["technical_id"])
        
        salary_details = {}
        salary_details["libelle"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer']/li[1]", parsed_job["technical_id"])
        parsed_job["salary"] = salary_details
        
        parsed_job["contract_type"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[1]", parsed_job["technical_id"])
        parsed_job["place"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[2]", parsed_job["technical_id"])
        parsed_job["publication_date"] = self.__try_to_find_text_of_element_by_xpath(div_offer, "//ul[@class = 'details-offer important-list']/li[@title = 'Date de publication']", parsed_job["technical_id"])

        return parsed_job

    @retry((TimeoutExceptionForDriverElements, ElementsNotFoundExceptionForDriver), tries=3, delay=1)
    def __parse_job_from_details_page(self, parsed_job: dict, page: int) -> dict :
        print("Scraping details of job " + parsed_job["technical_id"] + " for page " + page)
        # open web page
        self.driver.get(parsed_job["url"])
        
        # wait for element with name 'apec-detail-emploi' to be added        
        try:
            driverElements = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'date-offre') and contains(text(), 'Publiée le')]")))
        except TimeoutException:
            print("TimeoutException has been thrown for __parse_job_from_details_page() on job with ID" + parsed_job["technical_id"])
            raise TimeoutExceptionForDriverElements()
        
        if driverElements == None:
            print("ElementsNotFoundExceptionForDriver has been thrown for __parse_job_from_details_page() on job with ID" + parsed_job["technical_id"])
            raise ElementsNotFoundExceptionForDriver()
        
        description = ""
        description_in_p_tags = self.__try_to_find_elements_by_xpath(driverElements, "//div[@class='col-lg-8 border-L']/div[@class = 'details-post']/p", parsed_job["technical_id"])
        if len(description_in_p_tags) > 0:
            for p_tag in description_in_p_tags:
                description += p_tag.text
            
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
            print("Exception handled on element on job with ID " + technical_id + " searching by this XPATH :" + xpath)
            return ""
    
    def __try_to_find_elements_by_xpath(self, driverElements, xpath: str, technical_id):
        try:
            return driverElements.find_elements(By.XPATH, xpath)
        except NoSuchElementException:
            print("Exception handled on element on job with ID " + technical_id + "searching by this XPATH :" + xpath)
            return ""

    def __try_to_find_attribute_value_of_element_by_xpath(self, driverElements, xpath: str, attributeName: str, technical_id) -> str :
        try:
            return driverElements.find_element(By.XPATH, xpath).get_attribute(attributeName)
        except NoSuchElementException:
            print("Exception handled on element on job with ID " + technical_id + "searching by this XPATH :" + xpath)
            return ""
    
    def close_scraper(self):
        # quit webdriver
        self.driver.quit()