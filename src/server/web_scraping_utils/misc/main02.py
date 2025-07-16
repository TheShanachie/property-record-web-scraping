from web_scraping_utils import Driver, JSONCleaner
import concurrent.futures
import json, traceback, datetime
from jsonschema import validate, ValidationError

def scrape_records_by_address(address: str, pages: list, num_results: int):
    driver = Driver()
    results = driver.address_search(address, pages, num_results)
    driver.destroy()
    return results

# Set up the search queries.
pages = [
        "Parcel",
        "Owner",
        "Multi-Owner",
        "Residential",
        "Values",
        "Homestead",
        "Sales",
        "Land",
        # "Photos", # is currently not workin on larger queries.
    ] # Pages for the queries.
addresses = [(2835, "KUTER", None)] # ["Main St", "Wood St", "State St"] # Addresses for the queries.
arguments = [{'address':address, 'pages':pages, 'num_results':1} for address in addresses] # Arguments for the queries.

# Open some number of searches.
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations scrape the different calls.
    future_to_args = {executor.submit(scrape_records_by_address, **args): args for args in arguments}
    final_data = [] # Store the final json data elements.

    for future in concurrent.futures.as_completed(future_to_args):
        args = future_to_args[future]
        try:
            # collect the data.
            data = future.result()
            
            # Validate schema and clean the data.
            # for record in data:
            #     # Validate the heading schema.
            #     with open('./parsing/schema/heading.json', 'r') as f:
            #         JSONCleaner(json.load(f)).clean_validation(record['heading'])
                    
            #     # Validate the page data schema.
            #     with open('./parsing/schema/parcel.json', 'r') as f:
            #         JSONCleaner(json.load(f)).clean_validation(record['page-data']['Parcel'])
                
            #     # Validate the page data schema.
            #     with open('./parsing/schema/owner.json', 'r') as f:
            #         JSONCleaner(json.load(f)).clean_validation(record['page-data']['Owner'])
            
        except Exception as exc:
            print(f'{args} - generated an exception: {exc}')
            traceback.print_exception(exc)
        else:
            
            final_data.append(data)
                   
            
    # Store the data in a json @ '.' once done.
    current_datetime = datetime.datetime.now().timestamp()
    with open(f'scraped_data_{current_datetime}.json', 'w') as f:
        json.dump(final_data, f, indent=4)
        