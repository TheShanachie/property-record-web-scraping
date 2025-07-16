from api_access import get_tasks
from jsonschema.exceptions import ValidationError
import unittest, os, json

API_URL = os.environ.get('API_URL')

class TestTaskListEndpoint(unittest.TestCase):
           
    def test_tasks_endpoint(self):
        try:
            get_tasks(API_URL)
            
        except:
            self.fail("Test raised ExceptionType unexpectedly!")