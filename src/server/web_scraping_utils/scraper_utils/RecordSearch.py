import os.path, time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import Callable
from server.web_scraping_utils.scraper_utils.GetElement import expect_web_element, expect_web_elements, check_web_element
from server.web_scraping_utils.scraper_utils.CheckSite import is_address_search_page, is_address_search_page_results, is_record_page

def submit_address_search(driver: WebDriver, address: tuple):
    """
    Submits an address search using the provided WebDriver and address.
    This function fills out an address search form, submits it, and attempts to
    determine the number of search results. If successful, it clicks on the first
    property link in the search results.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
        address (tuple): This is a dictionary, whose values are the address components (number, street, direction).
    Returns:
        int: The number of search results if the search was successful and the number of results could be determined.
        None: If the search was not successful or the number of results could not be determined.
    """
    try:
        # Unpack variables from the address dict.
        number, street, direction = address
        
        # Fill out the number search form, can be none.
        if number is not None:
            number_input = expect_web_element(driver, args=(By.ID, "inpNumber"))
            number_input.clear()
            number_input.send_keys(number)
        
        # Fill out the address search form, cannot be none.
        street_input = expect_web_element(driver, args=(By.ID, "inpStreet"))
        street_input.clear()
        street_input.send_keys(street)
        
        # Fill out the direction search form if exists, can be none.
        # TODO: implement this behavior. This is a dropdown menu with name "inpAdrdir", and id "Select1".
        
        # Submit the form with the proper button
        options_row = expect_web_element(driver, args=(By.ID, "optionsRowElement"))
        submit_button = expect_web_element(options_row, args=(By.ID, "btSearch"))
        submit_button.click()
        
        # If this is a record page, then we are done, and the driver is ready to scrape.
        if is_record_page(driver):
            # Return 1 result, since we are on a record page.
            return 1
        
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