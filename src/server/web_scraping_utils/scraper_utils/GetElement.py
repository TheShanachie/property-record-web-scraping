from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from server.logging_utils import WebScrapeLogger

CHECK_ELEMENT_WAIT_TIME = 5
EXPECTED_ELEMENT_WAIT_TIME = 5
PAGE_LOAD_WAIT_TIME = 15 

def expect_web_element(
    driver: WebDriver, args: tuple, wait_time: float = EXPECTED_ELEMENT_WAIT_TIME
):
    try:
        # Wait for the element, then return it.
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(args)
        )

        # return the element.
        return element

    except Exception as e:

        # Log the unexpected behavior.
        WebScrapeLogger.error(f"Expected element via - '{args}' but it was not found.")

        # raise an exception if the element is not found.
        raise Exception(f"Expected element via - '{args}' but it was not found.") from e


def expect_web_elements(
    driver: WebDriver, args: tuple, wait_time: float = EXPECTED_ELEMENT_WAIT_TIME
):
    try:
        # Wait for the element, then return it.
        elements = WebDriverWait(driver, wait_time).until(
            EC.presence_of_all_elements_located(args)
        )

        # return the elements. (plural)
        return elements
    except Exception as e:

        # Log the unexpected behavior.
        WebScrapeLogger.error(f"Expected elements via - '{args}' but it was not found.")

        # raise exception and preserve the context.
        raise Exception(
            f"Expected elements via - '{args}' but it was not found."
        ) from e


def check_web_element(
    driver: WebDriver, args: tuple, wait_time: float = CHECK_ELEMENT_WAIT_TIME
):
    try:

        # Wait for the element, then return it.
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_all_elements_located(args)
        )

        # return the element.
        return driver.find_element(*args)

    except:

        # Assume that no element was found.
        # No error is raised since we assume that the element is optional.
        return None


def wait_for_page(
    driver: WebDriver, expected_index: int, wait_time: float = PAGE_LOAD_WAIT_TIME
):
    try:
        # Search Criteria
        search_criteria = (By.ID, "DTLNavigator_txtFromTo")

        # Wait for the element, then return it.
        WebDriverWait(driver, wait_time).until(
            EC.text_to_be_present_in_element_value(
                search_criteria, f"{expected_index} of"
            )  # Include the ' of' to avoid partial matches
        )
    except Exception as e:

        # Log the unexpected behavior.
        WebScrapeLogger.error(
            f"Expected record '{expected_index}' but it was not found."
        )

        # raise an exception and preserve the context.
        raise Exception(
            f"Expected record '{expected_index}' but it was not found."
        ) from e


def wait_for_subpage(
    driver: WebDriver, expected_page: str, wait_time: float = PAGE_LOAD_WAIT_TIME
):
    try:
        # Search Criteria
        xpath = f"//li[@class='sel' and a/span[text()='{expected_page}']]"
        search_criteria = (By.XPATH, xpath)

        # Wait for the element to have ID/Class
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(search_criteria)
        )
    except Exception as e:

        # Log the unexpected behavior.
        WebScrapeLogger.error(
            f"Expected subpage '{expected_page}' but it was not found."
        )

        # raise an exception and preserve the context.
        raise Exception(
            f"Expected subpage '{expected_page}' but it was not found."
        ) from e


def click_element(
    driver: WebDriver, args: tuple, wait_time: float = EXPECTED_ELEMENT_WAIT_TIME
):
    try:
        # Wait for the element to be clickable, then click it.
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(args)
        )

        # Remove styling.
        driver.execute_script("arguments[0].click();", element)

    except Exception as e:

        # Log the unexpected behavior.
        WebScrapeLogger.error(f"Error clicking element via - '{args}'.")

        # raise an exception and preserve the context.
        raise Exception(f"Error clicking element via - '{args}'." ) from e
