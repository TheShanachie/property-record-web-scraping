import os.path, time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import Callable
from .GetElement import expect_web_element, expect_web_elements, check_web_element
from LoggingUtils import WebScrapeLogger

def submit_address_search(driver: WebDriver, address: str):
    """
    Submits an address search using the provided WebDriver and address.
    This function fills out an address search form, submits it, and attempts to
    determine the number of search results. If successful, it clicks on the first
    property link in the search results.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
        address (str): The address to search for.
    Returns:
        int: The number of search results if the search was successful and the number of results could be determined.
        None: If the search was not successful or the number of results could not be determined.
    """
    try:
        
        # Fill out the address search form
        street_input = expect_web_element(driver, args=(By.ID, "inpStreet"))
        street_input.clear()
        street_input.send_keys(address)
        
        # Submit the form with the proper button
        options_row = expect_web_element(driver, args=(By.ID, "optionsRowElement"))
        submit_button = expect_web_element(options_row, args=(By.ID, "btSearch"))
        submit_button.click()
        
        # Is there big red banner text
        num_results_holder = None
        if check_web_element(driver, args=(By.CLASS_NAME, 'BannerTabsTextSelected')) is not None:
            # If there is big red text, meaning we found more than 500 results.
            num_results_holder = check_web_element(driver, args=(By.XPATH, "//ancestor::center//table[2]//td[3]//b[2]"))
            
        else:
            # There is no big red text and differnet order of elements.
            num_results_holder = check_web_element(driver, args=(By.XPATH, "//ancestor::center//table[1]//td[3]//b[2]"))
        
        # Return whether the search was successful and try to return the number of results
        if num_results_holder is not None:
            num_results = int(num_results_holder.text)
            property_link = driver.find_element(By.CLASS_NAME, "SearchResults")
            property_link.click()
            
            # Return the number of results and the driver is ready to scrape
            return num_results
        
        else:
            # Return nothing, the driver is in an unknown state
            return None
    
    except NoSuchElementException:
        
        # The search was not sucessful
        return None
    
    except ValueError:
        
        # The search was successful but the number of results could not be determined
        return None