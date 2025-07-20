import os.path, time, threading
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import Callable
from server.web_scraping_utils.scraper_utils.GetElement import expect_web_element, wait_for_page, wait_for_subpage
from server.logging_utils import web_scraping_core_logger
from server.web_scraping_utils.scraper_utils.RecordScraper import next_record, parse_record
from server.web_scraping_utils.scraper_utils.RecordSearch import submit_address_search
from server.config_utils import Config
from threading import Event

class Driver:
    """
    This class is used to create and direct a web scraping instance. This class should encapsulate
    all necessary logging, error handling, and web driver operations.
    ----------
    _id_counter : int
        Class variable to keep track of the last assigned id.
    url : str
        URL of the website to scrape.
    driver : WebDriver
        Chrome web driver instance.
    id : int
        Unique identifier for the driver instance.
    Methods
    -------
    __init__():
        Initializes the Driver instance with Chrome options and opens the website.
    apply(func: Callable, args: dict = None, log: bool = False):
        Applies a given function to the web driver with optional arguments and logging.
    pass_disclaimer(log: bool = False) -> bool:
        Passes the initial disclaimer on the website.
    address_search(address: str, pages: list, num_results: int = 1):
        Searches for an address on the website and collects data for a specified number of results.
    reset():
        Re-Initializes the Driver instance as if '__init__' has just been called
    """
    
    _id_counter = 0  # Class variable to keep track of the last assigned id
    
    def __init__(self):        
        try:
            ## Set up
            self.initialize()
            
        except Exception as e:
            
            # Log the error and return
            web_scraping_core_logger.error(msg="An Error was caught while initializing Driver Instance.")
            
            # Raise a new error and preserve the context
            raise Exception(f"Error initializing Driver Instance") from e
        
    def initialize(self):  
        # Get the configuration details
        self.config = Config.get_config("selenium_chrome")

        ## Setup chrome options
        self.chrome_options = Options()
        for arg in self.config["chrome-options"]:
            self.chrome_options.add_argument(arg)
            
        # Chrome options for user data
        self.chrome_options.add_argument("--no-first-run")
        self.chrome_options.add_argument("--disable-popup-blocking")
        self.chrome_options.add_argument("--incognito")

        # Set binary location for chrome
        self.chrome_options.binary_location = self.config["chrome-path"]
            
        ## Set path to chromedriver as per configuration
        self.webdriver_service = Service(self.config["chrome-driver-path"])
        
        ## Set the website path
        self.url = self.config["address-search-url"]
        
        ## Experimental options
        # This is for downloading files like images.
        self.config["experimental-chrome-options"]["download.default_directory"] = os.path.join(os.getcwd(), self.config["experimental-chrome-options"]["download.default_directory"])
        self.chrome_options.add_experimental_option("prefs", self.config["experimental-chrome-options"])            
        
        # Choose Chrome Browser
        self.driver = webdriver.Chrome(
            service=self.webdriver_service, 
            options=self.chrome_options
        )
        
        # Open the website
        self.driver.get(self.url)
        
        # Assign a unique id to the instance
        self.id = Driver._id_counter
        Driver._id_counter += 1
        
        # Success message
        web_scraping_core_logger.info(msg=f"Driver instance initialized with id - {self.id}")
        
    def health(self) -> dict:
        """
        Checks the health of the driver instance.
        Returns:
            dict: A dictionary containing the status of the driver instance.
        """
        try:
            # Check if the driver is still alive
            if self.driver.service.is_connectable():
                return {"status": "healthy",
                        "id": self.id,
                        "url": self.driver.current_url,
                        "title": self.driver.title,
                        }
            else:
                return {"status": "unhealthy", "id": self.id}
        except Exception as e:
            # Log the error
            web_scraping_core_logger.error(msg=f"Error checking health of driver instance {self.id}")
            return {"status": "error", "id": self.id, "error": str(e)}
        
            
   
    def apply(self, func: Callable, args: dict = None, log: bool = False):
        """
        Applies a given function to the driver with optional arguments and logging.
        Args:
            func (Callable): The function to be applied to the driver.
            args (dict, optional): A dictionary of arguments to pass to the function. Defaults to None.
            log (bool, optional): If True, logs the function application process. Defaults to False.
        Returns:
            Any: The result of the function applied to the driver, or None if an exception occurs.
        Logs:
            Logs the function application process and any errors encountered if logging is enabled.
        """
        
        try:
            # log if needed  
            if log:
                web_scraping_core_logger.info(msg=f"Applying function '{func.__name__}' on driver id - {self.id}")
                        
            # Apply with args or not
            if args is not None:
                result = func(self.driver, **args)
            else:
                result = func(self.driver)
            return result
        
        except Exception as e:
            
            # Log the error.
            web_scraping_core_logger.error(msg=f"Error applying function '{func.__name__}' on driver id - {self.id}")
            
            # Raaise a new error and preserve the context
            raise Exception(f"Error applying function '{func.__name__}'") from e
        

    def pass_disclaimer(self):
        """
        Attempts to pass the initial disclaimer on the webpage by clicking the agree button.
        Args:
            log (bool): If True, logs the action and any errors encountered. Default is False.
        Returns:
            bool: True if the disclaimer was successfully passed, False otherwise.
        """
        
        try:
            
            # This passes the initial disclaimer
            expect_web_element(self.driver, args=(By.ID, "btAgree")).click()
            
            # Return True if the disclaimer was passed
            return True
                    
        except Exception as e:
            
            # Log the error
            web_scraping_core_logger.error(msg="Error passing the disclaimer")
            
            # Raise a new error and preserve the context
            raise Exception("Error passing the disclaimer") from e
            
        
    def address_search(self, address: tuple, pages: list, num_results: int = 1, quit_event: threading.Event = None):
        """
        Perform an address search and collect data from the specified number of results. 
        Args:
            address (tuple): The address to search for.
            pages (list): A list of pages to parse for each result.
            num_results (int, optional): The number of results to collect. Defaults to 1.
        Returns:
            list: A list of collected data for each result. Returns an empty list if no results.
        """
        try: 
            # Pass the discalimer
            if not self.pass_disclaimer():
                web_scraping_core_logger.error(msg=f"In Driver instance {self.id}, unsuccessful in passing the disclaimer.")
                return None # Did not get past the disclaimer
            
            # Submit the address
            if self.apply(func=submit_address_search, args={"address": address}) is None:
                web_scraping_core_logger.warning(msg=f"In Driver instance {self.id}, address search not successful.")
                return None # Did not get past the address search
            
            # Collect the data for number of results
            results = []
            for index in range(1,num_results+1):
                
                # If the quit event is true, return here.
                if quit_event and quit_event.is_set():
                    break
                
                # For each page, collect the data
                record_data = self.apply(func=parse_record, args={"pages": pages})
                
                # Something went wrong. Break the loop
                if record_data is None:
                    web_scraping_core_logger.warning(msg=f"In Driver instance {self.id}, record parsing exited after {index} records.")
                    break
                
                # Append the current record to final results
                results.append(record_data)
                
                # Success message
                web_scraping_core_logger.info(msg=f"In Driver instance {self.id}, data successfully collected for record {index} of {num_results} with head: {record_data['heading']}")
                
                # Get the next record
                self.apply(func=next_record, args={"record_index": index+1})
                
            # Return the final results
            return results
        
        except Exception as e:
            
                # TODO: This is for debugging and should be removed in prod
                # print("There was an error scraping address in driver.")

                # Get the root cause of the error
                current_exception = e
                chain = []
                while current_exception is not None:
                    chain.append(current_exception)
                    current_exception = current_exception.__cause__
                root_error = chain[-1] if chain else None
                
                # If the error was a selenium timeout error
                ## In this case, we need to return the partial results.
                ## This type of error is unfortunately common, and we need to handle it gracefully.
                if isinstance(root_error, TimeoutException):
                    # Log the behavior
                    web_scraping_core_logger.warning(msg=f"In Driver instance {self.id}, address search timed out after {len(results)} records.")
                    
                    # Return the partial results
                    if 'results' in locals():
                        return results
                
                # Otherwise, the error was some other exception
                else: 
                    # Log the error
                    web_scraping_core_logger.error(msg=f"Error in address search for driver instance {self.id}")
                    
                    # Raise a new error and preserve the context
                    raise Exception(f"Error in address search for driver instance {self.id}") from e
                
    def reset(self):
        try:
            # TODO: This functionality can and must be made more efficient. Do later.
            
            # Re-initialize object.
            self.initialize()
            
        except Exception as e:
            
            # Log the error and return
            web_scraping_core_logger.error(msg="An Error was caught while re-initializing Driver Instance.")
            
            # Raise a new error and preserve the context
            raise Exception(f"Error Reseting Driver Instance") from e
        
        
    def destroy(self):
        try:
            self.driver.quit()
        except: 
            return