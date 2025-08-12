from selenium.webdriver.common.by import By
from property_record_web_scraping.server.web_scraping_utils.scraper_utils.GetElement import check_web_element


def is_address_search_page(driver) -> bool:
    """Return whether the driver is on the address search page."""
    try:
        # Check if the driver is on the address search page.
        search_text_path = "//button[contains(@id, 'btSearch')]" # If this exists, then the driver is on the address search page.
        return check_web_element(driver, args=(By.XPATH, search_text_path)) is not None
    
    except:
        # Don't care what exception it is, just return None.
        return False

def is_address_search_page_results(driver) -> bool:
    """
    Return whether the driver is on an address search page, and showing results.
    """
    try:
        # check if the driver is on the address search page.
        if not is_address_search_page(driver):
            return False
        
        # Check if the driver is on the address search page and has results.
        search_results_path = "//table[contains(@id, 'searchResults')]" # If this exists and on the address search page, then there are results.
        return check_web_element(driver, args=(By.XPATH, search_results_path)) is not None
    
    except:
        return 

def is_record_page(driver) -> bool:
    """
    Return whether the driver is on a record page.
    """

    try:
        # Check if the driver is on a record page.
        parcel_pages_indication_path = "//input[contains(@id, 'DTLNavigator_txtFromTo')]" # If this exists, then the driver is on a record page.
        return check_web_element(driver, args=(By.XPATH, parcel_pages_indication_path)) is not None
    
    except: # Don't care what exception it is, just return None.
        return False
