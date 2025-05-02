import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_text_from_class(url, class_name):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all elements with the specified class name
        elements = soup.find_all(class_=class_name)
        
        # Extract and return the text from all <a> tags within each element
        texts = []
        for element in elements:
            a_tags = element.find_all('a')
            for a_tag in a_tags:
                texts.append(a_tag.get_text())
        return texts
    else:
        print(f"Failed to retrieve the URL: {response.status_code}")
        return []

# Example usage
url = 'https://geographic.org/streetview/usa/pa/northampton/northampton.html'
class_name = 'listspan'
texts = get_text_from_class(url, class_name)

# Create a pandas Series from the list of texts
address_series = pd.Series(texts)

# Save the Series to a Parquet file
address_series.to_frame(name='address').to_parquet('addresses.parquet')