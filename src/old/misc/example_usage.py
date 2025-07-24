from logging_utils import web_scraping_core_logger
from scraper_utils import Driver, submit_address_search
from scraper_utils.RecordScraper import parse_record_tables, go_to_record_page, get_record_heading, get_listing_index, next_record
from scraper_utils.Driver import Driver


def scenario_1():
    web_scraping_core_logger.info(msg="Begin Example/Test Scenario 1")
    web_scraping_core_logger.info(msg="End Example/Test Scenario 1")


def scenario_2():
    web_scraping_core_logger.info(msg="Begin Example/Test Scenario 2")
    driver = Driver()
    driver.pass_disclaimer()
    web_scraping_core_logger.info(msg="End Example/Test Scenario 2")


def scenario_3():
    web_scraping_core_logger.info(msg="Begin Example/Test Scenario 4")
    driver = Driver()
    driver.pass_disclaimer()
    result = driver.apply(func=submit_address_search, args={"address": "Main St"})
    web_scraping_core_logger.info(msg=f"Result - {result}")
    web_scraping_core_logger.info(msg="End Example/Test Scenario 4")


def scenario_4():
    web_scraping_core_logger.info(msg="Begin Example/Test Scenario 4")
    driver = Driver()
    driver.pass_disclaimer()
    result = driver.apply(func=submit_address_search, args={"address": "Main St"})
    result = driver.apply(func=parse_record_tables)
    web_scraping_core_logger.info(msg=f"Result - {result}")
    web_scraping_core_logger.info(msg="End Example/Test Scenario 4")


def scenario_5():
    web_scraping_core_logger.info(msg="Begin Example/Test Scenario 5")
    driver = Driver()
    driver.pass_disclaimer()
    driver.apply(func=submit_address_search, args={"address": "Main St"})

    # For record pages
    pages = ["Parcel", "Owner"]  # First two pages; non-generic

    # For each page, show that we can parse through
    page_data = {}
    for page in pages:
        web_scraping_core_logger.info(msg=f"Processing page - {page}")
        driver.apply(func=go_to_record_page, args={"page": page})
        page_data[page] = driver.apply(func=parse_record_tables)
        web_scraping_core_logger.info(
            msg=f"Successful Page Parsing - Result - {page_data[page]}"
        )

    # Log the final result
    web_scraping_core_logger.info(msg=f"Result - {page_data}")
    web_scraping_core_logger.info(msg="End Example/Test Scenario 5")


def scenario_6():
    web_scraping_core_logger.info(msg="Begin Example/Test Scenario 6")
    driver = Driver()
    driver.pass_disclaimer()
    driver.apply(func=submit_address_search, args={"address": "Main St"})

    # For record pages
    pages = [
        "Parcel",
        "Owner",
        "Multi-Owner",
        "Residential",
        "Values",
        "Homestead",
        "Sales",
        "Land",
    ]  # First two pages; non-generic

    # For each page, show that we can parse through
    page_data = {}
    for page in pages:
        web_scraping_core_logger.info(msg=f"Processing page - {page}")
        driver.apply(func=go_to_record_page, args={"page": page})
        page_data[page] = driver.apply(func=parse_record_tables)
        web_scraping_core_logger.info(
            msg=f"Successful Page Parsing - Result - {page_data[page]}"
        )

    # Log the final result
    web_scraping_core_logger.info(msg=f"Result - {page_data}")
    web_scraping_core_logger.info(msg="End Example/Test Scenario 6")


def scenario_7():
    web_scraping_core_logger.info(msg="Begin Example/Test Scenario 7")
    driver = Driver()
    driver.pass_disclaimer()
    driver.apply(func=submit_address_search, args={"address": "Main St"})

    # For record pages
    pages = [
        "Parcel",
        "Owner",
        "Multi-Owner",
        "Residential",
        "Values",
        "Homestead",
        "Sales",
        "Land",
    ]  # First two pages; non-generic

    # Iterate through some actual records
    number_of_records = 50
    for index in range(number_of_records):
        web_scraping_core_logger.info(msg=f"Processing Record - {index}")
        # driver.apply(func=get_record_heading)
        
        # For each page, show that we can parse through
        page_data = {}
        for page in pages:
            web_scraping_core_logger.info(msg=f"Processing page '{page}' for record '{index}'")
            driver.apply(func=go_to_record_page, args={"page": page})
            page_data[page] = driver.apply(func=parse_record_tables)
            web_scraping_core_logger.info(
                msg=f"Successful Page Parsing - Result - {page_data[page]}"
            )
            
        web_scraping_core_logger.info(msg=f"Result (Record {index} of {number_of_records}) - {page_data}")
        
        # Get the next record 
        driver.apply(func=next_record)
    # End
    web_scraping_core_logger.info(msg="End Example/Test Scenario 7")