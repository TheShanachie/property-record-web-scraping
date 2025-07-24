from api_access import submit_scrape_job, scrape_job_status, get_tasks, get_health
import unittest, os, time, json
from test.logger import test_logger

API_URL = os.environ.get('API_URL')

class TestValidSubmitTask(unittest.TestCase):
    
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

    def _create_example_tasks(self) -> dict:
        tasks = []
        for address in [
            (103, "Main St", ""),
            # (102, "Main St", ""),
            # (103, "Main St", "")
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
    
    def _poll_task(self, task_id: str, pause: int = 30, timeout: int = 3600):
        """ Poll for the task status until it completes or times out. """
        
        # Log the start of the polling.
        test_logger.info(f"Starting polling for task {task_id}: {pause} seconds pause, {timeout} seconds timeout.")

        start_time = time.time()
        while True:
            response = scrape_job_status(API_URL, task_id)
            print(f"Polling task {task_id}: {json.dumps(response, indent=4)}")
            totaltime = time.time() - start_time
            if response["metadata"]['status'] == "completed":
                test_logger.info(f"Task {task_id} completed in {totaltime:.2f} seconds. Response: {json.dumps(response, indent=4)}")
                return response
            if response["metadata"]["status"] in ["failed", "cancelled"]:
                test_logger.info(f"Task {task_id} failed or was cancelled after {totaltime:.2f} seconds. Response: {json.dumps(response, indent=4)}")
                raise Exception()
            if time.time() - start_time > timeout: 
                test_logger.info(f"Task {task_id} did not complete within the timeout period of {timeout} seconds. Response: {json.dumps(response, indent=4)}")
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds.")
            health_info = get_health(API_URL)
            test_logger.info(f"Task {task_id} is still running. Status: {response['metadata']['status']}. Health info: {json.dumps(health_info, indent=4)}. Waiting for {pause} seconds before next poll.")
            time.sleep(pause)
        
    def test_generic_valid_task_output(self):
        """
            Test that the output of a valid task submission is as expected. 
            Poll the task and check the metadata, until it is completed.
        """
        
        try:
            
            tasks = self._create_example_tasks()
            for task in tasks:
                response = self._submit_task(task)
                
                self.assertEqual(response["status_code"], 200)
                
                # Poll the task until it is completed
                task_id = response["metadata"]['id']
                result = self._poll_task(task_id)
                
                # Check that the result is as expected
                self.assertEqual(result["metadata"]['status'], "completed")
                self.assertIsNotNone(result["metadata"]['result'])
        
        except TimeoutError as e:
            
            self.fail(f"Task did not complete within the timeout period: {str(e)}")