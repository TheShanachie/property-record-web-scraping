import os.path, time, re, json
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

DEFAULT_WAIT_TIME = 5

def wait_for_web_el(driver: WebDriver, args: tuple, wait_time: float = DEFAULT_WAIT_TIME, returns: bool = False):
    try:
        # Wait for the element, then return it.
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_all_elements_located(args)
        )
        
        # return the element.
        return driver.find_element(*args)
    except:
        if returns is False:
            print(f"ERROR: There was an error waiting for element via - {args}")
            exit(1)
            
        else:
            raise Exception(f"There was an error waiting for element via - {args}")
        

def wait_for_web_els(driver: WebDriver, args: tuple, wait_time: float = DEFAULT_WAIT_TIME, returns: bool = False):
    try:
        # Wait for the element, then return it.
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_all_elements_located(args)
        )
        
        # return the elements. (plural)
        return driver.find_elements(*args)
    except:
        if returns is False:
            print(f"ERROR: There was an error waiting for elements via - {args}")
            exit(1)
            
        else:
            raise Exception(f"There was an error waiting for elements via - {args}")
        

# TODO: DOCUMENT! DOCUMENT! DOCUMENT! None of this even makes sense to me. I'm scared.
class SeleniumWrapper:
    def __init__(self):
        ## Setup chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ensure GUI is off
        chrome_options.add_argument("--no-sandbox")
        
        # Set path to chromedriver as per your configuration
        homedir = os.path.expanduser("~")
        chrome_options.binary_location = f"{homedir}/chrome-linux64/chrome"
        webdriver_service = Service(f"{homedir}/chromedriver-linux64/chromedriver")

        # Choose Chrome Browser
        self.driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    
    # This can be used later to check about page details...  
    def check_page(self):
        # menu = self.wait_for_web_el(self.)
        menu = wait_for_web_el(self.driver, args=(By.ID, "topmenu"))
        selected = wait_for_web_el(menu, args=(By.CLASS_NAME, "sel")).text
        if (selected == "Property Records"):
            nav = wait_for_web_el(self.driver, args=(By.ID, "sidemenu"))
            subpage = wait_for_web_el(nav, args=(By.CLASS_NAME, "sel")).text
        return selected, subpage
        

    def submit_address_search(self, street: str):
        """ This is a nightmare and I'm scared."""
        try:
            # Get page
            self.driver.get("https://www.ncpub.org/_web/Search/Disclaimer.aspx?FromUrl=../search/commonsearch.aspx?mode=address")

            # Click the "I Agree" button
            wait_for_web_el(self.driver, args=(By.ID, "btAgree")).click()
            
            # Fill out the form
            street_input = wait_for_web_el(self.driver, args=(By.ID, "inpStreet"))
            street_input.clear()
            street_input.send_keys(street)

            # Select "50" from the selPageSize dropdown
            page_size_select = wait_for_web_el(self.driver, args=(By.ID, "selPageSize"))
            for option in wait_for_web_els(page_size_select, args=(By.TAG_NAME, 'option')):
                if option.text == '50':
                    option.click()
                break

            # Submit the form
            options_row = wait_for_web_el(self.driver, args=(By.ID, "optionsRowElement"))
            submit_button = wait_for_web_el(options_row, args=(By.ID, "btSearch"))
            submit_button.click()

            # Wait for the search results to load
            # lower - 'searchResults' holds the entire table of upper-'SearchResults'
            # Return whether the search was successful and try to return the number of results
            num_properties = int( wait_for_web_el(self.driver, args=(By.XPATH, "//ancestor::center//table[2]//td[3]//b[2]")).text )
            property_link = self.driver.find_element(By.CLASS_NAME, "SearchResults")
            property_link.click()
            return True, num_properties
        
        except NoSuchElementException:
            # The search was not sucessful
            return False, None
        
        except ValueError:
            # The search was successful but the number of results could not be determined
            return True, None
        
        
    # TODO: Document this parsing routine for collecting from card sliders
    def iter_card_arrow(self, table):
        try:
            # If the arrow exists
            arrow = wait_for_web_el(table, args=(By.XPATH, ".//*[@title='next page']"), returns=True)
            if (arrow == None or arrow.is_displayed()):
                return arrow
            else:
                return None
        except NoSuchElementException:
            return None
        
        
    def read_section_card(self, table):
        headings = [x.text for x in wait_for_web_els(table, args=(By.CLASS_NAME, "DataletSideHeading"))]
        datas = [x.text for x in wait_for_web_els(table, args=(By.CLASS_NAME, "DataletData"))]
        return dict(zip(headings, datas))
            
            
    def parse_datalet_table(self, index: int, datalet_id: str):
        # Two possibilites
        ## 1) This exists in datalet div
        ## 2) There is no datalet div, wrapping this item
        
        table_data = {}
        table_num = 0
        while True:
            # Get the two internal tables: (Expecting most common behavior)
            print("Page:", self.check_page(), "Section:", datalet_id.removeprefix("datalet_div_"), "Element:", table_num)
            tables = []
            
            ## 1st possibility: The tables are surrounded by the datalet_divs
            try: 
                datalet = wait_for_web_el(self.driver, args=(By.ID, datalet_id), wait_time=0, returns=True) # Get the datalet each time because the page is reloaded.
                tables.extend( wait_for_web_els(datalet, args=(By.XPATH, "./table"), returns=True) ) # This is printing trh error message 
        
                # Check whether the behavior is as expected
                if (len(tables) != 2):
                    print(f"Unexpected number of tables in datalet... {len(tables)} were found.")
                    return None
            
            ## 2nd possibilty: The tables are not surrounded by the datalet divs
            except:
                holder = wait_for_web_el(self.driver, args=(By.CLASS_NAME, "holder"))
                tables.extend([wait_for_web_el(holder, args=(By.XPATH, f"./table[{((index) * 2)+1}]")), 
                               wait_for_web_el(holder, args=(By.XPATH, f"./table[{((index) * 2)+2}]")) ] )
            
            ## Proceed with the desired tables
            table_data[f"table_{table_num}"] = self.read_section_card(tables[1])
            next_arrow = self.iter_card_arrow(tables[0])
            if (next_arrow == None):
                return {"table name": tables[1].get_attribute("id"),
                        "table data": table_data}
            else:
                table_num += 1
                next_arrow.click()
    
            
    def parse_datalet_tables(self, page_name: str):
        self.go_to_property_page(page_name)
        datalets = wait_for_web_els(self.driver, args=(By.XPATH, "//div[starts-with(@id, 'datalet_div_')]"), returns=True)
        if datalets is not None:
            ids = [x.get_attribute("id") for x in datalets]
            result = {}
            for index, datalet_id in enumerate(ids):
                result[f"section{index}"] = self.parse_datalet_table(index, datalet_id)
            return result
        
    def go_to_property_page(self, page_name):
        try:
            wait_for_web_el(self.driver, args=(By.XPATH, f"//*[text()='{page_name}']")).click()
            return True
        except:
            print(f"ERROR: Invalid page name. You're trying to access {page_name} on a property page, but this page name is not listed.")
            return False
        
        
    def current_property_head(self):
        # Assuming you're on a property page
        header = wait_for_web_el(self.driver, args=(By.ID, "datalet_header_row"))
        top =  wait_for_web_els(header, args=(By.CLASS_NAME, "DataletHeaderTop"))
        btm =  wait_for_web_els(header, args=(By.CLASS_NAME, "DataletHeaderBottom"))
        return {"PARID": top[0].text.removeprefix("PARDID: "),
                "OWNER": btm[1].text.removesuffix(","),
                "ADDRESS": btm[2].text}
        
    
    def current_listing_index(self):
        widget_bar = wait_for_web_el(self.driver, args=(By.ID, "DTLNavigator_txtFromTo"))
        try:
            return [int(x) for x in widget_bar.get_attribute("value").split("of")]
        except:
            return None        
        
    def next_record_listing(self):
        try:
            # Get and click the next button
            next_btn = wait_for_web_el(self.driver, args=(By.ID, "DTLNavigator_imageNext"))
            next_btn.click()
            
            # Get listing index
            index = self.current_listing_index()[1]
            return index
        except:
            # Create error strategies
            return
        
    
    def parse_current_record(self, pages: list):
        # Scrape from the pages listed
        result = {}
        for page in pages:
            result[page] = self.parse_datalet_tables(page)
            
        # return the results
        return result
    
    
    def parse_results(self, pages: list):
        results = {}
        _, total = self.current_listing_index()
        for n in range(100):
            print(f"Parse record {n+1} of {total}")
            results[f"Record_{n}"] = self.parse_current_record(pages)
            print(results[f"Record_{n}"])
            self.next_record_listing()
            
        return results
            
        

# Example usage...
wrapper = SeleniumWrapper()
address = "Main St"
pages=["Parcel", "Owner", "Multi-Owner", "Residential", "Values", "Homestead", "Sales", "Land"]
_, num_results = wrapper.submit_address_search(address)
print("Number of address search results:",  num_results)
results = wrapper.parse_results(pages)
with open("data.json", 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)
wrapper.driver.quit()

