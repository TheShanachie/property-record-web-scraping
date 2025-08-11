from test.tests.base_test import BaseAPITest
from test.test_utilities.logger import test_logger
import json

class TestValidSubmitTask(BaseAPITest):
    """ Test cases for valid task submissions. """
    
    def test_single_task_with_model_validation(self):
        """Test single task submission with full model validation"""
        
        # Create validated input
        scrape_input = self.create_test_scrape_input(
            address=(101, "Main St", ""),
            pages=[],
            num_results=1
        )
        
        # Submit task
        response = self.client.submit_scrape_job(scrape_input.model_dump())
        
        # Log the response
        test_logger.debug(f"response: {json.dumps(response.model_dump(), indent=2)}")
        
        # Validate response structure
        self.assertValidResponse(response, 200)
        self.assertIsNotNone(response.metadata.id)
        
        # Verify that the task ID is in the tasks list
        tasks = self.client.get_tasks().tasks
        task_ids = [task.id for task in tasks]
        self.assertIn(response.metadata.id, task_ids)
        
        # Poll for completion
        task_id = response.metadata.id
        final_response = self.poll_until_complete(task_id)
        
        # Validate completion
        self.assertTaskCompleted(final_response)
        
        # Validate result structure
        self.assertIsInstance(final_response['metadata']['result'], list)
        self.assertGreater(len(final_response['metadata']['result']), -1)
        
        # Validate each result item
        for result_item in final_response['metadata']['result']:
            self.assertIn('heading', result_item)
            self.assertIn('page_data', result_item)
    
    def test_multiple_tasks_concurrent(self):
        """Test multiple tasks with model validation"""
        
        tasks = []
        task_ids = []
        
        # Submit multiple tasks
        for i in range(3):
            scrape_input = self.create_test_scrape_input(
                address=(101 + i, "Main St", ""),
                pages=[],
                num_results=1
            )
            
            response = self.client.submit_scrape_job(scrape_input.model_dump())
            self.assertValidResponse(response, 200)
            
            tasks.append(response)
            task_ids.append(response.metadata.id)
        
        # Poll all tasks to completion
        for task_id in task_ids:
            final_response = self.poll_until_complete(task_id)
            self.assertTaskCompleted(final_response)