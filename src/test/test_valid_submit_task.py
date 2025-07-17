from api_access import submit_scrape_job, scrape_job_status, get_tasks
import unittest, os, time, json

API_URL = os.environ.get('API_URL')

class TestValidSubmitTask(unittest.TestCase):

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
    
    def _poll_task(self, task_id: str, pause: int = 10, timeout: int = 3600):
        """ Poll for the task status until it completes or times out. """
        
        start_time = time.time()
        while True:
            response = scrape_job_status(API_URL, task_id)
            # print(f"Polling task {task_id}: {response['status_code']}, {response['metadata']['status']}", flush=True)
            print(response, flush=True)
            print()
            print()
            if response["metadata"]['status'] == "completed":
                return response
            if response["metadata"]["status"] in ["failed", "cancelled"]:
                print(json.dumps(response, indent=4))
                raise Exception()
            if time.time() - start_time > timeout: 
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds.")
            time.sleep(pause)
        
    
    def test_generic_valid_task(self):
        """
        Test a valid task submission. We don't pass any pages, so it should only scrape the heading for the address.
        """
        tasks = self._create_example_tasks()
        for task in tasks:
            response = self._submit_task(task)
            print(json.dumps(response, indent=4))
            print(flush=True)
            self.assertEqual(response["status_code"], 200)
            
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