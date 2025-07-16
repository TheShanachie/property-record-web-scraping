from api_access import submit_scrape_job
from jsonschema.exceptions import ValidationError
import unittest
import os

API_URL = os.environ.get('API_URL')

class TestSubmitTaskEndpoint(unittest.TestCase):

    def _create_example_tasks(self) -> dict:
        tasks = []
        for address in [
            (101, "Main St", ""),
            (102, "Main St", ""),
            (103, "Main St", "")
        ]:
            tasks.append({
                "address": address,
                "pages": [],  # Only scrape the heading for the address, show that it works
                "max_results": 1
            })
        return tasks

    def _submit_task(self, data: dict):
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
        print(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": 1
        }))
        
        # Extra fields
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": 1,
            "extra_field": "This should not be here"
        })["status_code"], 500)

        # Missing fields
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", "")
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "pages": []
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "max_results": 1
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "pages": [],
            "max_results": 1
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": []
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "max_results": 1
        })["status_code"], 500)

    def test_invalid_arguments_type(self):
        """
        The expected types of the arguments are:
        - address: tuple of (int, str, str)
        - pages: list
        - max_results: int
        If the types are not correct, a ValueError should be raised.
        """
        # Invalid address type
        self.assertEqual(self._submit_task({
            "address": "101 Main St",
            "pages": [],
            "max_results": 1
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": 101,
            "pages": [],
            "max_results": 1
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": {"number": 101, "street": "Main St", "dir": ""},
            "pages": [],
            "max_results": 1
        })["status_code"], 500)

        # Invalid pages type
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": 101,
            "max_results": 1
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": "This should be a list",
            "max_results": 1
        })["status_code"], 500)

        # Invalid max_results type
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": "This should be an int"
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ""),
            "pages": [],
            "max_results": ("This should be an int", 1)
        })["status_code"], 500)

    def test_invalid_address_values(self):
        """
        The expected values of the address tuple are:
        - number: int
        - street: str
        - dir: str
        If the values are not correct, a ValueError should be raised.
        """
        # Invalid number
        self.assertEqual(self._submit_task({
            "address": ("101", "Main St", ""),
            "pages": [],
            "max_results": 1
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": (101.5, "Main St", ""),
            "pages": [],
            "max_results": 1
        })["status_code"], 500)

        # Invalid street
        self.assertEqual(self._submit_task({
            "address": (101, 123, ""),
            "pages": [],
            "max_results": 1
        })["status_code"], 500)

        # Invalid dir
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", ()),
            "pages": [],
            "max_results": 1
        })["status_code"], 500)
        self.assertEqual(self._submit_task({
            "address": (101, "Main St", 123),
            "pages": [],
            "max_results": 1
        })["status_code"], 500)

    def test_invalid_pages(self):
        pass

    def test_invalid_max_results(self):
        pass

    def test_submit_task_invalid(self):
        # Test the submission of an invalid task
        pass
