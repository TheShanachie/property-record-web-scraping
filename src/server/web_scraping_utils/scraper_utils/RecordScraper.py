from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import urllib, time, os, re
from server.web_scraping_utils.scraper_utils.GetElement import expect_web_element, expect_web_elements, check_web_element, wait_for_subpage, wait_for_page, click_element
from selenium.webdriver.common.action_chains import ActionChains
from server.logging_utils import web_scraping_core_logger
from server.web_scraping_utils.scraper_utils.PhotoScraper import scrape_photo_page

def parse_record_card(table: WebDriver) -> dict:
    """
    Parses a record card from a web table element.
    Args:
        table (WebDriver): The web table element containing the record card data.
    Returns:
        dict: A dictionary where the keys are the headings and the values are the corresponding data from the table.
              Returns None if an exception occurs during parsing.
    """
    try:
        headings = [
            x.text
            for x in expect_web_elements(
                table, args=(By.CLASS_NAME, "DataletSideHeading")
            )
        ]
        datas = [
            x.text
            for x in expect_web_elements(table, args=(By.CLASS_NAME, "DataletData"))
        ]
        return dict(zip(headings, datas))
    except Exception as e:
        
        # Log the error
        web_scraping_core_logger.error("Error parsing record card")
        
        # Raise the error and preserve the context
        raise Exception("Error parsing record card") from e


def parse_record_tables(driver: WebDriver) -> dict:
    """
    Parses record tables from a web page using a Selenium WebDriver.
    This function navigates through pairs of tables within a specified
    section of a web page, extracts data from each table, and returns
    the collected data in a structured format.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to
                            interact with the web page.
    Returns:
        dict: A dictionary containing the parsed data from each section
              of the record tables. The keys are the section labels.
              Returns None if an exception occurs during parsing.
    Raises:
        Exception: Catches and prints any exception that occurs during
                   the parsing process.
    """
    
    try:

        # result data
        result_data = {}

        # Loop through the tables in pairs
        num_tables = len(
            expect_web_elements(
                driver,
                args=(
                    By.XPATH,
                    "//div[contains(@class, 'holder')]/table  \
                    | //div[contains(@class, 'holder')]/*/table",
                ),
            )
        )

        for index in range(int(num_tables / 2)):

            # Store the table data
            table_data = []

            # Loop through all possible cards in a particular record page section
            while True:
                # Get the holder element
                tables = expect_web_elements(
                    driver,
                    args=(
                        By.XPATH,
                        "//div[contains(@class, 'holder')]/table  \
                    | //div[contains(@class, 'holder')]/*/table",
                    ),
                )

                # Get the top and bottom table for a particular record page section
                top_table = tables[2 * index]
                bottom_table = tables[(2 * index) + 1]                
                
                # Remove anything after the first digit in the section label.
                sectionLabel = top_table.text
                for i, char in enumerate(sectionLabel):
                    if char.isdigit():
                        sectionLabel = sectionLabel[:i]
                        break

                # Parse the bottom table for information
                card_result = parse_record_card(bottom_table)

                # Append the table card data to the result
                table_data.append(card_result)

                # Parse the top table for data naming + card arrows
                if is_table_card_arrow(top_table):

                    # Press the arrow and loop to collect the next card.
                    press_table_card_arrow(top_table)

                else:
                    # Exit the loop when all cards in the table have been noted.
                    break

            # Store the table data in the result after the inner loop
            result_data[f"{sectionLabel}"] = table_data

        # Return the resulting data
        return result_data

    except Exception as e:
            
        # Log the error
        web_scraping_core_logger.error("Error parsing record tables")
        
        # Raise the error and preserve the context
        raise Exception("Error parsing record tables") from e


def go_to_record_page(driver: WebDriver, page: str) -> None:
    """
    Navigates to a specific record page using the provided WebDriver instance. 
    This function expects exact matches for the record page string and the string found in the website navigation menu.
    TODO: Why does this function search page name in entire page content? Expand XPATH?
    Args:
        driver (WebDriver): The WebDriver instance used to interact with the web page.
        page (str): The name of the record page to navigate to.
    Raises:
        Exception: If the specified record page is not found.
    """
    
    try:
        expect_web_element(driver, args=(By.XPATH, f"//*[text()='{page}']")).click()
        wait_for_subpage(driver, page)
    except Exception as e:
        
        # Log the error
        web_scraping_core_logger.error("Error navigating to record page")
        
        # Raise the error and preserve the context
        raise Exception(f"Error navigating to record page: {page}") from e


def is_table_card_arrow(driver: WebDriver) -> bool:
    """
    Checks if the 'next page' arrow element is present on the web page. This function finds the first 
    element matching the XPath expression './/*[@title='next page']', regardless of the web driver provided.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
    Returns:
        bool: True if the 'next page' arrow element is found, False otherwise.
    """
    try: 
        return (
            check_web_element(driver, args=(By.XPATH, ".//*[@title='next page']"))
            is not None
        )
    except Exception as e:
            
        # Log the error
        web_scraping_core_logger.error("Error checking for table card arrow")
        
        # Raise the error and preserve the context
        raise Exception("Error checking for table card arrow") from e


def next_record(driver: WebDriver, record_index: int) -> int | None:
    """
    Navigates to the next record in a web-based record system using a Selenium WebDriver.
    Note: This page moves to the Parcel Page and then clicks the next button to go to the next record.
    This is because the next page will take much too long if it has to generate photos again. We don't
    want the server side to throttle or anything.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
        record_index (int): The current index of the record being processed.
    Returns:
        int | None: The index of the next record if successful, or None if an error occurs.
    """
    
    try:
        # Go to Parcel page
        go_to_record_page(driver, "Parcel")
        
        # Wait for the sub page.
        wait_for_subpage(driver, "Parcel")
        
        # Click the next button to go to the next page
        click_element(driver, args=(By.ID, "DTLNavigator_imageNext"))
        
        # Wait for the page to load.
        wait_for_page(driver, record_index)

        # Get listing index
        index = get_listing_index(driver)[1]
        return index
    except Exception as e:
        
        # Log the error
        web_scraping_core_logger.error("Error navigating to next record")
        
        # Raise the error and preserve the context
        raise Exception("Error navigating to next record") from e


def press_table_card_arrow(driver: WebDriver) -> None:
    """
    Presses the arrow button to navigate to the next page in a table card. This function assumes that
    an arrow element is present on the web page and finds the first element matching the XPath expression.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
    """
    try:
        expect_web_element(driver, args=(By.XPATH, ".//*[@title='next page']")).click()
    except Exception as e:
        # Log the error
        web_scraping_core_logger.error("Error pressing table card arrow")
        
        # Raise the error and preserve the context
        raise Exception("Error pressing table card arrow") from e


def parse_record(driver: WebDriver, pages: list) -> dict:
    """
    Parses a record by navigating through multiple pages and collecting data.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web pages.
        pages (list): A list of page identifiers or URLs to navigate and collect data from.
    Returns:
        dict: A dictionary containing the record data with the following structure:
            {
                "heading": str,  # The heading of the record
                "page_data": {
                    page: dict  # Data collected from each page
                }
            }
        If an exception occurs during parsing, returns None.
    """
    try: 
        # Record to fill
        record = {"heading": get_record_heading(driver), "page_data": {}}

        # For each page, collect the data
        for page in pages:
            go_to_record_page(driver, page)
            if page == "Photos":
                record["page_data"][page] = scrape_photo_page(driver)
            else:
                record["page_data"][page] = parse_record_tables(driver)

        # Return the record
        return record
    except Exception as e:
        
        # Log the error
        web_scraping_core_logger.error("Error parsing record")
        
        # Raise the error and preserve the context
        raise Exception("Error parsing record") from e


def get_record_heading(driver: WebDriver):
    """
    Extracts and returns the record heading information from a property page.
    Args:
        driver (WebDriver): The Selenium WebDriver instance used to interact with the web page.
    Returns:
        dict: A dictionary containing the following keys:
            - "PARID": The property/parcel ID extracted from the header.
            - "OWNER": The owner's name extracted from the header.
            - "ADDRESS": The cleaned address extracted from the header.
    Helper Function:
        clean_string(input_string: str, character: str) -> str:
            Removes the part of the input string before and including the specified character,
            and returns the cleaned string with leading whitespace removed.
    Assumptions:
        - The function assumes that the driver is already on a property page.
        - The function expects specific HTML elements with IDs and class names to be present on the page.
    """
    # Small helper function because I'm dumb and this took me forever to figure out somehow
    def clean_string(input_string, character):
        position = input_string.find(character)
        if position == -1:
            return input_string
        result = input_string[position + 1 :]
        return result.lstrip()

    try:
        # Assuming you're on a property page
        header = expect_web_element(driver, args=(By.ID, "datalet_header_row"))
        top = expect_web_element(header, args=(By.CLASS_NAME, "DataletHeaderTop"))
        btm = expect_web_elements(header, args=(By.CLASS_NAME, "DataletHeaderBottom"))
        result = {
            "PARID": top.text.removeprefix("PARID: "),
            "OWNER": btm[1].text.removesuffix(","),
            "ADDRESS": clean_string(btm[0].text, ","),
        }
        return result
    except Exception as e:
        # Log the error
        web_scraping_core_logger.error("Error getting record heading")
        
        # Raise the error and preserve the context
        raise Exception("Error getting record heading") from e


def get_listing_index(driver: WebDriver):
    """
    Retrieves the current listing index from a web element in the provided WebDriver instance.
    Args:
        driver (WebDriver): The WebDriver instance used to interact with the web page.
    Returns:
        list: A list containing two integers representing the current listing index and the total number of listings.
              Returns None if the web element is not found or an error occurs.
    """
    try:
        widget_bar = expect_web_element(driver, args=(By.ID, "DTLNavigator_txtFromTo"))
        return [int(x) for x in widget_bar.get_attribute("value").split("of")]
    except Exception as e:
        # Log the error
        web_scraping_core_logger.error("Error getting listing index")
        
        # Raise the error and preserve the context
        raise Exception("Error getting listing index") from e
