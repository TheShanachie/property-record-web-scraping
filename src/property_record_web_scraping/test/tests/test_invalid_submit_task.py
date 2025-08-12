from property_record_web_scraping.test.tests.base_test import BaseAPITest
from property_record_web_scraping.test.test_utilities.logger import test_logger
from pydantic import BaseModel


class TestInvalidSubmitTask(BaseAPITest):
    """
    Test cases for invalid task submissions.
    This class extends BaseAPITest to leverage common test setup and validation methods.
    """
    
    def _assert_response_status(self, response: dict | BaseModel, expected_status: int):
        """
        Helper method to assert the response status code.
        """
        if isinstance(response, BaseModel):
            response = response.model_dump()
        self.assertIsInstance(response, (dict, BaseModel))
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
                "num_results": 1,
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
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "pages": [],
                "num_results": 1
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
                "num_results": 1
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
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": 101,
                "pages": [],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": {"number": 101, "street": "Main St", "dir": ""},
                "pages": [],
                "num_results": 1
            }), 400
        )

        # Invalid pages type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": 101,
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": "This should be a list",
                "num_results": 1
            }), 400
        )

        # Invalid num_results type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "num_results": "This should be an int"
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "num_results": ("This should be an int", 1)
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
                "num_results": 1
            }), 200  # Pydantic will coerce str to int if possible
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101.5, "Main St", ""),
                "pages": [],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (-101, "Main St", ""),
                "pages": [],
                "num_results": 1
            }), 400
        )

        # Invalid street
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, 123, ""),
                "pages": [],
                "num_results": 1
            }), 400
        )

        # Invalid dir
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ()),
                "pages": [],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", 123),
                "pages": [],
                "num_results": 1
            }), 400
        )
        
        # Invalid address tuple length
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St"),
                "pages": [],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", "", "Extra value"),
                "pages": [],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (),
                "pages": [],
                "num_results": 1
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
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": 123,
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": None,
                "num_results": 1
            }), 400
        )

        # Invalid page content
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [123],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [None],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [{"page": 1}],
                "num_results": 1
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": ["owner"],
                "num_results": 1
            }), 400
        )
        
    def test_invalid_num_results(self):
        """
        Test for invalid num_results in task submission.
        """
        
        # Invalid num_results type
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "num_results": "This should be an int"
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "num_results": 1.5
            }), 400
        )
        self._assert_response_status(
            self.client.submit_scrape_job({
                "address": (101, "Main St", ""),
                "pages": [],
                "num_results": -1
            }), 400
        )
