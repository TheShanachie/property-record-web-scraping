import unittest, os, json
from test.test_utilities.logger import test_logger

from test.tests.base_test import BaseAPITest
class TestInvalidSubmitTask(BaseAPITest):
    """
    Test cases for invalid task submissions.
    This class extends BaseAPITest to leverage common test setup and validation methods.
    """
    
    def _assert_response_status(self, response: dict, expected_status: int):
        """
        Helper method to assert the response status code.
        """
        self.assertIsInstance(response, dict)
        self.assertIn('status_code', response)
        self.assertEqual(response['status_code'], expected_status)
        

    def test_invalid_arguments_shape(self):
        """
        Test for invalid argument shapes in task submission.
        """
        
        # Extra fields
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "max_results": 1,
                "extra_field": "This should not be here"
            }), 400
        )
        
        # Missing fields
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", "")
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "pages": []
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "pages": [],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": []
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "max_results": 1
            }), 400
        ) 
        
    def test_invalid_arguments_type(self):
        """
        Test for invalid argument types in task submission.
        """
        
        # Invalid address type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": "101 Main St",
                "pages": [],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": 101,
                "pages": [],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": {"number": 101, "street": "Main St", "dir": ""},
                "pages": [],
                "max_results": 1
            }), 400
        )

        # Invalid pages type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": 101,
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": "This should be a list",
                "max_results": 1
            }), 400
        )

        # Invalid max_results type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "max_results": "This should be an int"
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "max_results": ("This should be an int", 1)
            }), 400
        )
            
    
    def test_invalid_address_values(self):
        """
        Test for invalid address values in task submission.
        """
        
        # Invalid number
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": ("101", "Main St", ""),
                "pages": [],
                "max_results": 1
            }), 200  # Pydantic will coerce str to int if possible
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101.5, "Main St", ""),
                "pages": [],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (-101, "Main St", ""),
                "pages": [],
                "max_results": 1
            }), 400
        )

        # Invalid street
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, 123, ""),
                "pages": [],
                "max_results": 1
            }), 400
        )

        # Invalid dir
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ()),
                "pages": [],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", 123),
                "pages": [],
                "max_results": 1
            }), 400
        )
        
        # Invalid address tuple length
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St"),
                "pages": [],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", "", "Extra value"),
                "pages": [],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (),
                "pages": [],
                "max_results": 1
            }), 400
        )
        
    def test_invalid_pages(self):
        """
        Test for invalid pages in task submission.
        """
        
        # Invalid pages type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": "This should be a list",
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": 123,
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": None,
                "max_results": 1
            }), 400
        )

        # Invalid page content
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [123],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [None],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [{"page": 1}],
                "max_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": ["owner"],
                "max_results": 1
            }), 400
        )
        
    def test_invalid_max_results(self):
        """
        Test for invalid max_results in task submission.
        """
        
        # Invalid max_results type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "max_results": "This should be an int"
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "max_results": 1.5
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "max_results": -1
            }), 400
        )
