from api_access import submit_scrape_job, get_health    
from jsonschema.exceptions import ValidationError
import unittest, os, json
from test.logger import test_logger

API_URL = os.environ.get('API_URL')

class TestInvalidSubmitTask(unittest.TestCase):
    
    def setUp(self):
        """
        Set up the test environment, if needed. 
        Log the start of the test.
        """
        health_info = get_health(API_URL)
        test_logger.info(f"Starting test {__class__.__name__}. Health info: {json.dumps(health_info, indent=4)}")

    def tearDown(self):
        """
        Clean up after the test, if needed.
        Log the end of the test.
        """
        health_info = get_health(API_URL)
        test_logger.info(f"Completed test {__class__.__name__}. Health info: {json.dumps(health_info, indent=4)}")

    def _submit_task(self, data: dict):
        test_logger.info(f"Submitting task with data: {data}")
        response = submit_scrape_job(API_URL, data)
        return response

    def test_invalid_arguments_shape(self):
        """ 
        The expected shape of the arguments is:
        {
            "address": (int, str, str),
            "pages": list,
            "max_results": int
        }
        If the shape is not correct, a ValueError should be raised.
        """
        
        # Logging the test start
        test_logger.info("Starting test for invalid arguments shape")
        
        # Extra fields
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": 1,
            "extra_field": "This should not be here"
        })["status_code"], 400)

        # Missing fields
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", "")
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "pages": []
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": []
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "max_results": 1
        })["status_code"], 400)
        
        # Logging the test completion
        test_logger.info("Completed test for invalid arguments shape")

    def test_invalid_arguments_type(self):
        """
        The expected types of the arguments are:
        - address: tuple of (int, str, str)
        - pages: list
        - max_results: int
        If the types are not correct, a ValueError should be raised.
        """
        
        # Logging the test start
        test_logger.info("Starting test for invalid arguments type")
        
        # Invalid address type
        self.assertEqual(self._submit_task({
            "address": "101 Main St",
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": 101,
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": {"number": 101, "street": "Main St", "dir": ""},
            "pages": [],
            "max_results": 1
        })["status_code"], 400)

        # Invalid pages type
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": 101,
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": "This should be a list",
            "max_results": 1
        })["status_code"], 400)

        # Invalid max_results type
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": "This should be an int"
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": ("This should be an int", 1)
        })["status_code"], 400)
        
        # Logging the test completion
        test_logger.info("Completed test for invalid arguments type")

    def test_invalid_address_values(self):
        """
        The expected values of the address tuple are:
        - number: int
        - street: str
        - dir: str
        If the values are not correct, a ValueError should be raised.
        """
        
        # Logging the test start
        test_logger.info("Starting test for invalid address values")
        
        # Invalid number
        self.assertEqual(self._submit_task({
            "address": ("101", "Main St", ""),
            "pages": [],
            "max_results": 1
        })["status_code"], 200) # Pydandic will coence str to int if possible
        self.assertEqual(self._submit_task({
            "address": (101.5, "Main St", ""),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (-101, "Main St", 123),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)

        # Invalid street
        self.assertEqual(self._submit_task({
            "address": (101, 123, ""),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)

        # Invalid dir
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ()),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", 123),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        
        # Invalid address tuple length
        self.assertEqual(self._submit_task({
            "address": (101, "Main St"),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", "", "Extra value"),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (),
            "pages": [],
            "max_results": 1
        })["status_code"], 400)
        
        # Logging the test completion
        test_logger.info("Completed test for invalid address values")

    def test_invalid_pages(self):
        """
            The expected values of the address tuple are:
            - number: int
            - street: str
            - dir: str
            If the values are not correct, a ValueError should be raised.
        """
        
        # Logging the test start
        test_logger.info("Starting test for invalid pages")
        
        # Invalid pages type
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": "This should be a list",
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": 123,
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": None,
            "max_results": 1
        })["status_code"], 400)

        # Invalid page content
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [123],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [None],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [{"page": 1}],
            "max_results": 1
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": ["owner"],
            "max_results": 1
        })["status_code"], 400)
        
        # Logging the test completion
        test_logger.info("Completed test for invalid pages")
        

    def test_invalid_max_results(self):
        """
            The expected values of the address tuple are:
            - number: int
            - street: str
            - dir: str
            If the values are not correct, a ValueError should be raised.
        """
        
        # Logging the test start
        test_logger.info("Starting test for invalid max_results")
        
        # Invalid max_results type
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": "This should be an int"
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": 1.5
        })["status_code"], 400)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": -1
        })["status_code"], 400)
        
        # Logging the test completion
        test_logger.info("Completed test for invalid max_results")
