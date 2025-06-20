from api_access import get_tasks
from parsing import JSONSchemaRegistry
from jsonschema.exceptions import ValidationError
import unittest, os, json

API_URL = os.environ.get('API_URL')
API_SCHEMA_DIR_PATH = os.environ.get('API_SCHEMA_DIR_PATH')
schema_registry = JSONSchemaRegistry(directory=API_SCHEMA_DIR_PATH)

class TestTaskListEndpoint(unittest.TestCase):
           
    def test_tasks_endpoint(self):
        try:
            get_tasks(API_URL)
        except:
            self.fail("Test raised ExceptionType unexpectedly!")
    
    def test_tasks_endpoint_response(self):
        try:
            response = get_tasks(API_URL)            
            schema_registry.validate(schema='api_schema/output/tasks.json', data=response)
            
        except ValidationError as error:
            self.fail("ValidationError raised via jsonschema validation.")
        
        except:
            self.fail("Methods raised exception unexpectedly!")