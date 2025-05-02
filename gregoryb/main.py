from ScraperUtils.Driver import Driver
import concurrent.futures
from LoggingUtils import WebScrapeLogger, RecordLogger
import json, traceback


def scrape_records_by_address(address: str, pages: list, num_results: int):
    driver = Driver()
    results = driver.address_search(address, pages, num_results)
    driver.destroy()
    return results

# Set up the search queries.
pages = ["Parcel"] # Pages for the queries.
addresses = ["Main St", "Wood St"]# ["Main St", "Wood St", "State St"] # Addresses for the queries.
arguments = [{'address':address, 'pages':pages, 'num_results':2} for address in addresses] # Arguments for the queries.

# Open some number of searches.
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations scrape the different calls.
    future_to_args = {executor.submit(scrape_records_by_address, **args): args for args in arguments}
    for future in concurrent.futures.as_completed(future_to_args):
        args = future_to_args[future]
        try:
            data = future.result()
        except Exception as exc:
            print(f'{args} - generated an exception: {exc}')
            traceback.print_exception(exc)
        else:
            print(f'{args} - data: {data}')
        