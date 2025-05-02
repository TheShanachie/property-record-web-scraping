from LoggingUtils import WebScrapeLogger
from ScraperUtils import Driver, submit_address_search
from ScraperUtils.RecordScraper import parse_record_tables, go_to_record_page, get_record_heading, get_listing_index, next_record
from ScraperUtils.Driver import Driver


def scenario_1():
    WebScrapeLogger.info(msg="Begin Example/Test Scenario 1")
    WebScrapeLogger.info(msg="End Example/Test Scenario 1")


def scenario_2():
    WebScrapeLogger.info(msg="Begin Example/Test Scenario 2")
    driver = Driver()
    driver.pass_disclaimer()
    WebScrapeLogger.info(msg="End Example/Test Scenario 2")


def scenario_3():
    WebScrapeLogger.info(msg="Begin Example/Test Scenario 4")
    driver = Driver()
    driver.pass_disclaimer()
    result = driver.apply(func=submit_address_search, args={"address": "Main St"})
    WebScrapeLogger.info(msg=f"Result - {result}")
    WebScrapeLogger.info(msg="End Example/Test Scenario 4")


def scenario_4():
    WebScrapeLogger.info(msg="Begin Example/Test Scenario 4")
    driver = Driver()
    driver.pass_disclaimer()
    result = driver.apply(func=submit_address_search, args={"address": "Main St"})
    result = driver.apply(func=parse_record_tables)
    WebScrapeLogger.info(msg=f"Result - {result}")
    WebScrapeLogger.info(msg="End Example/Test Scenario 4")


def scenario_5():
    WebScrapeLogger.info(msg="Begin Example/Test Scenario 5")
    driver = Driver()
    driver.pass_disclaimer()
    driver.apply(func=submit_address_search, args={"address": "Main St"})

    # For record pages
    pages = ["Parcel", "Owner"]  # First two pages; non-generic

    # For each page, show that we can parse through
    page_data = {}
    for page in pages:
        WebScrapeLogger.info(msg=f"Processing page - {page}")
        driver.apply(func=go_to_record_page, args={"page": page})
        page_data[page] = driver.apply(func=parse_record_tables)
        WebScrapeLogger.info(
            msg=f"Successful Page Parsing - Result - {page_data[page]}"
        )

    # Log the final result
    WebScrapeLogger.info(msg=f"Result - {page_data}")
    WebScrapeLogger.info(msg="End Example/Test Scenario 5")


def scenario_6():
    WebScrapeLogger.info(msg="Begin Example/Test Scenario 6")
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
        WebScrapeLogger.info(msg=f"Processing page - {page}")
        driver.apply(func=go_to_record_page, args={"page": page})
        page_data[page] = driver.apply(func=parse_record_tables)
        WebScrapeLogger.info(
            msg=f"Successful Page Parsing - Result - {page_data[page]}"
        )

    # Log the final result
    WebScrapeLogger.info(msg=f"Result - {page_data}")
    WebScrapeLogger.info(msg="End Example/Test Scenario 6")


def scenario_7():
    WebScrapeLogger.info(msg="Begin Example/Test Scenario 7")
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
        WebScrapeLogger.info(msg=f"Processing Record - {index}")
        # driver.apply(func=get_record_heading)
        
        # For each page, show that we can parse through
        page_data = {}
        for page in pages:
            WebScrapeLogger.info(msg=f"Processing page '{page}' for record '{index}'")
            driver.apply(func=go_to_record_page, args={"page": page})
            page_data[page] = driver.apply(func=parse_record_tables)
            WebScrapeLogger.info(
                msg=f"Successful Page Parsing - Result - {page_data[page]}"
            )
            
        WebScrapeLogger.info(msg=f"Result (Record {index} of {number_of_records}) - {page_data}")
        
        # Get the next record 
        driver.apply(func=next_record)
    # End
    WebScrapeLogger.info(msg="End Example/Test Scenario 7")