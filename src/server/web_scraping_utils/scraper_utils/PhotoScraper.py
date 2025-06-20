from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import urllib, time, os, re, cv2, base64, numpy as np, PIL
from .GetElement import expect_web_element, expect_web_elements, check_web_element, wait_for_subpage, click_element
from selenium.webdriver.common.action_chains import ActionChains
from ..logging_utils import WebScrapeLogger

# Function to encode image to base64
def encode_image_to_base64(image_path: str) -> str:
    try: 
        # Load the image using OpenCV
        image = cv2.imread(image_path)

        # Encode the image to base64
        _, image_bytes = cv2.imencode(".jpg", image)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return image_base64
    except Exception as e:
        # Log the error
        WebScrapeLogger.error("Error encoding image to base64")
        
        # Raise the error and preserve the context
        raise Exception("Error encoding image to base64") from e


# Function to decode base64 string to image
def decode_base64_to_image(image_base64: str) -> np.ndarray:
    try:
        # Decode the base64 string back to an image
        image_bytes_decoded = base64.b64decode(image_base64)
        image_decoded = cv2.imdecode(np.frombuffer(image_bytes_decoded, np.uint8), cv2.IMREAD_COLOR)
        return image_decoded
    except Exception as e:
        # Log the error
        WebScrapeLogger.error("Error decoding base64 to image")
        
        # Raise the error and preserve the context
        raise Exception("Error decoding base64 to image") from e


# Function to scrape the current photo at a record Photos page.
def scrape_current_photo(driver: WebDriver):
    try: 
        # Some variables.
        ## This is hardcoded for now, but should be part of the config called in 'Driver' constructor.
        download_dir = "./Logs/TempEmpty"  # Directory where the downloaded file will be saved.    
        
        # This function expects some conditions prior to execution:
        ## The download directory must exist.
        download_dir_exists = os.path.exists(os.path.join(os.getcwd(), download_dir))   
        assert download_dir_exists, "Download directory does not exist." 
        
        ## The download directory must be empty.
        download_dir_empty = len(os.listdir(download_dir)) == 0
        assert download_dir_empty, "Download directory is not empty."
        
        # Function to wait for download to complete
        def wait_for_download(timeout=30):
                time.sleep(30)
                seconds = 0
                dl_wait = True
                while dl_wait and seconds < timeout:
                    time.sleep(1)
                    dl_wait = False
                    for fname in os.listdir(download_dir):
                        if fname.endswith('.crdownload'):
                            dl_wait = True
                    seconds += 1
                return seconds < timeout
            
        # Function to get the downloaded file.
        def get_downloaded_file():
            # There should only be one file in the directory.
            img_file = os.listdir(download_dir)[0]
            img = encode_image_to_base64(os.path.join(download_dir, img_file))
            return img       
            
        # Function to remove downloaded file.
        def remove_downloaded_file():
            try:
                for file in os.listdir(download_dir):
                    os.remove(os.path.join(download_dir, file))
            except:
                return   
    
        # Download the current photo.
        xpath = "//div[contains(@class, 'dm-left')]//a[contains(@id, 'download')]"
        click_element(driver, args=(By.XPATH, xpath))
        
        # Wait for the download to complete.
        download_succeeded = wait_for_download()
        
        # If the download succeeded, get the downloaded file & clean the downloaddir.
        if download_succeeded:
            img = get_downloaded_file()
            remove_downloaded_file()
            return img
        else:
            # Raise an excpetion if the download failed, because this bevahior is unexpected.
            raise Exception("Image download failed")
            
    except Exception as e:
        
        # Log the error
        WebScrapeLogger.error("Error scraping current photo")
        
        # Raise the error and preserve the context
        raise Exception("Error scraping current photo") from e


def scrape_photo_page(driver: WebDriver) -> list:
    try:
        # Get the number of images and details.
        xpath = "//ul[contains(@id, 'dm-imagelist')]"
        image_list = expect_web_element(driver, args=(By.XPATH, xpath))
        
        # Get child image elements.
        image_elements = expect_web_elements(image_list, args=(By.XPATH, "./li"))
        
        # Return list
        images = []
        
        # Build the image jsons.
        for idx, image_element in enumerate(image_elements):
                       
            # Get the metadata
            metadata_path = "//table[contains(@class, 'dm-metadata')]"
            metadata_str = expect_web_element(image_element, args=(By.XPATH, metadata_path)).text
            
            # Select the current image.
            driver.execute_script("arguments[0].click();", image_element)
            
            # Sleep for a bit to allow the image to load.
            time.sleep(5)
            
            # Get the image.
            image = scrape_current_photo(driver)
            
            # Construct the image json.
            image_json = {
                "image": image,
                "metadata": metadata_str,
            }
            
            # Append the image json to the list.
            images.append(image_json)
            
        # Return the list of images.
        return images
            
    except Exception as e:
        
        # Log the error
        WebScrapeLogger.error("Error scraping photo page")
        
        # Raise the error and preserve the context
        raise Exception("Error scraping photo page") from e