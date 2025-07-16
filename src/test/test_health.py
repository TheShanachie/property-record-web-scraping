from api_access import get_health
from jsonschema.exceptions import ValidationError
import unittest, os

API_URL = os.environ.get('API_URL') 

class TestHealthEndpoint(unittest.TestCase):
           
    def test_health_endpoint(self):
        try:
            get_health(API_URL)
        except:
            self.fail("Test raised ExceptionType unexpectedly!")