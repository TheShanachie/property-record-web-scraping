from web_scraping_utils import Driver, JSONCleaner
import json, sys

# List of addresses which cumulatively cover all behaviors and org types.
# Organize by the address pages that are covered. This can give some feel 
# for which addresses work and such.
test_records = {
    "Parcel": [
            (2835, "KUTER", None),
            (500, "MAIN ST", None),
            (700, "MAIN ST", None),
        ],
    "Owner": [
            (2835, "KUTER", None),
            (500, "MAIN ST", None),
            (700, "MAIN ST", None),
        ],
    "Multi-Owner": [
            (2835, "KUTER", None),
        ],
    "Residential": [
            (2835, "KUTER", None),
        ],
    "Commercial": [
            (500, "MAIN ST", None),
            (700, "MAIN ST", None),
            (511, "3rd St", None),
            (530, "3rd St", None),
        ],
    "Out Buildings": [
            (530, "3rd St", None),
        ],
    "Land": [
            (2835, "KUTER", None),
            (500, "MAIN ST", None),
            (700, "MAIN ST", None),
        ],
    "Values": [
            (2835, "KUTER", None),
            (500, "MAIN ST", None),
            (700, "MAIN ST", None),
        ],
    "Homestead": [
            (2835, "KUTER", None),
        ],
    "Sales": [
            (2835, "KUTER", None),
            (500, "MAIN ST", None),
            (700, "MAIN ST", None),
        ],
    "Photos": [],
}

# The input data is a list of all unqiue addresses.
test_addresses = list(set([item for sublist in test_records.values() for item in sublist]))

# Print the test addresss data and relevant details.
print()
print("Test Address Details:")
print(" Total Addresses:", len(test_addresses))
print(" Addresses...")
for index, address in enumerate(test_addresses):
    print(f"    Address {index}: {address[0]} {address[1]} {address[2] if address[2] else ''}")
    
# print seperator.
print("\n" + "-" * 50 + "\n")

# Load a JSON cleaner for each page type.
json_cleaners = {
    "Heading": "./web_scraping_utils/parsing/schema/heading.json",
    "Parcel": "./web_scraping_utils/parsing/schema/parcel.json",
    "Owner": "./web_scraping_utils/parsing/schema/owner.json",
    "Multi-Owner": "./web_scraping_utils/parsing/schema/multi_owner.json",
    "Residential": "./web_scraping_utils/parsing/schema/residential.json",
    # "Commercial": "./web_scraping_utils/parsing/schema/commercial.json",
    # "Out Buildings": "./web_scraping_utils/parsing/schema/out_buildings.json",
    "Land": "./web_scraping_utils/parsing/schema/land.json",
    "Values": "./web_scraping_utils/parsing/schema/values.json",
    "Homestead": "./web_scraping_utils/parsing/schema/homestead.json",
    "Sales": "./web_scraping_utils/parsing/schema/sales.json",
    # "Photos": "./web_scraping_utils/parsing/schema/photos.json",
}

for page, schema_path in json_cleaners.items():
    with open(schema_path, 'r') as file:
        json_cleaners[page] = JSONCleaner(json.load(file))
        print(f"Loaded JSON Cleaner for {page} from {schema_path}")
print("JSON Cleaner Objects Loaded Successfully.")

# print seperator.
print("\n" + "-" * 50 + "\n")

# Function to scrape records for a single address.
def scrape_single_address(address: tuple):
    try:
        pages = ["Parcel", "Owner", "Multi-Owner", "Residential", "Land", "Values", "Homestead", "Sales"]  # Pages for the queries.
        driver = Driver()
        results = driver.address_search(address, pages, num_results=1)
        driver.destroy()
        return results
    except Exception as e:
        print(f"Error scraping address {address}: {e}")
        return []

# Function to validate and clean the results.
def validate_address_results(results):
    # Validate the results for each page type.
    for record in results:
        # Validate the heading schema.
        json_cleaners["Heading"].clean_validation(record['heading'])
        
        # Validate each page data schema.
        for page, data in record['page-data'].items():
            if page in json_cleaners:
                json_cleaners[page].clean_validation(data)
            else:
                print(f"Warning: No JSON cleaner for page '{page}'.")
    return True


print("Starting Address Scraping and Validation Tests...")

# Iterate through each address and scrape results.
for address in test_addresses:
    print(f"Scraping address: {address[0]} {address[1]} {address[2] if address[2] else ''}")
    results = scrape_single_address(address)
    print(f"Result size {address}: {sys.getsizeof(results)} bytes")
    
    # Validate the results.
    validate_address_results(results)
    print(f"Validation successful for address: {address[0]} {address[1]} {address[2] if address[2] else ''}")

print("All tests completed.")

