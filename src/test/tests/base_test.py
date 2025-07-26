
import unittest
import os
from test.test_utilities.api_client import APIClient
from server.models import ActionInput, ActionOutput
from typing import Tuple, Optional

class BaseAPITest(unittest.TestCase):
    """Base test class with model validation support"""
    
    @classmethod
    def setUpClass(cls):
        cls.api_url = os.environ.get('API_URL', 'http://localhost:5000/api/v1')
        cls.client = APIClient(cls.api_url)
        
    def setUp(self):
        """ Set up method, making sure the api accessable for all test. """
        self.assertTrue(self.client.active_base_url(), "API base URL is not active")
    
    def assertValidResponse(self, response: ActionOutput.OutputModel, expected_status: int = 200):
        """Assert response is valid and has expected status"""
        self.assertIsInstance(response, ActionOutput.OutputModel)
        self.assertEqual(response.status_code, expected_status)
        
        if expected_status == 200:
            self.assertIsNone(response.error)
            self.assertIsNotNone(response.metadata)
        else:
            self.assertIsNotNone(response.error)
    
    def assertTaskCompleted(self, response: ActionOutput.OutputModel):
        """Assert task has completed successfully"""
        self.assertValidResponse(response, 200)
        self.assertEqual(response.metadata.status, "completed")
        self.assertIsNotNone(response.metadata.result)
        self.assertIsNotNone(response.metadata.finished_at)
    
    def create_test_scrape_input(self, address: Tuple[int, str, str], pages: list = [], max_results: int = 1) -> ActionInput.Scrape:
        """Create a valid test scrape input"""
        if pages is None:
            pages = []
        
        return ActionInput.Scrape(
            address=address,
            pages=pages,
            max_results=max_results
        )
    
    def poll_until_complete(self, task_id: str, timeout: int = 300, poll_interval: int = 5) -> ActionOutput.OutputModel:
        """Poll task until completion with proper model validation"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.client.get_task_status(task_id)
            self.assertValidResponse(response, 200)
            
            if response.metadata.status in ["completed", "failed", "cancelled"]:
                return response
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")