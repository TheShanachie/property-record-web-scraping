from api_access import get_health
from jsonschema.exceptions import ValidationError
import unittest, os, json
from test.logger import test_logger

API_URL = os.environ.get('API_URL') 

class TestHealthEndpoint(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment, if needed. 
        Log the start of the test.
        """
        health_info = get_health(API_URL)
        test_logger.debug(f"Starting test {__class__.__name__}. Health info: {json.dumps(health_info, indent=4)}")

    def tearDown(self):
        """
        Clean up after the test, if needed.
        Log the end of the test.
        """
        health_info = get_health(API_URL)
        test_logger.debug(f"Completed test {__class__.__name__}. Health info: {json.dumps(health_info, indent=4)}")
           
    def test_health_endpoint(self):
        try:
            get_health(API_URL)
        except:
            test_logger.error("Error occurred while testing health endpoint")   
            self.fail("Test raised ExceptionType unexpectedly!")