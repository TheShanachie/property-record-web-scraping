from test.tests.base_test import BaseAPITest
from test.test_utilities.logger import test_logger
from typing import Optional
import json


class TestValidSubmitTaskWithPages(BaseAPITest):
    """ Test cases for valid task submissions. """
    submitted_tasks = {}

    def _expect_task(self, task_id: str):
        """ 
        Expect that a task is running and will finish. Use the internal mapping of expected pages
        that is updated during task creation to validate the response is as expected.        
        """
        assert task_id in self.submitted_tasks, f"Task ID {task_id} not found in submitted tasks"
        response = self.poll_until_complete(task_id, timeout=1800)
        self.assertIn("metadata", response)
        self.assertIn("result", response['metadata'])
        self.assertIsNotNone(response['metadata']['result'])
        self.assertGreater(len(response['metadata']['result']), 0)
        for record in response['metadata']['result']:
            self.assertValidRecord(record, self.submitted_tasks[task_id])
        test_logger.debug(f"Task {task_id} completed successfully. The response data is as follows:")
        test_logger.debug(json.dumps(response, indent=4))

    def _expect_tasks(self):
        """ 
        Expect all tasks that are in the submitted_tasks mapping to be running and finish successfully.
        Use the internal mapping of task pages, to validate as response was formed as expected.
        """
        for task_id in self.submitted_tasks:
            self._expect_task(task_id)

    def _submit_task(self, address: tuple, expected_pages: Optional[list] = []):
        """ 
        Submit a task to the API and log details with the internal mapping. We assume that 
        the inputs to this method do not cause errors with the api call and the pages are
        valid.
        """
        task_data = self.create_test_scrape_input(address=address, pages=expected_pages, num_results=1)
        response = self.client.submit_scrape_job(task_data.model_dump())
        self.submitted_tasks.update({response.metadata.id: expected_pages})

    def _get_example_task_stats(self):
        """ Get a dictionary of stats for the example tasks """
        example_tasks = self._get_example_tasks()
        example_task_stats = {
            possible_page: 0
            for possible_page
            in ["Parcel", "Owner", "Multi-Owner", "Residential", "Land", "Values", "Homestead", "Sales"]}
        for example_task in example_tasks:
            _, pages = example_task
            for page in pages:
                if page in example_task_stats:
                    example_task_stats[page] += 1
                else:
                    example_task_stats[page] = 1
        return example_task_stats

    def _get_example_tasks(self):
        """ Provide a list of example tasks for the API. """
        return [((2835, "KUTER", ""), ["Parcel", "Owner", "Multi-Owner", "Residential", "Land", "Values", "Homestead", "Sales"]),
                ((500, "MAIN ST", ""), ["Parcel", "Owner", "Land", "Values", "Sales"]),  # "Commercial"
                ((700, "MAIN ST", ""), ["Parcel", "Owner", "Land", "Values", "Sales"]),  # "Commercial"
                ((511, "3rd St", ""), ["Sales"]),  # "Commercial"
                ((530, "3rd St", ""), ["Sales"])  # "Commercial", "Out Buildings"
                ]

    def test_submit_task_with_pages(self):
        """ Test that we can submit tasks and retrieve the expected data once the tasks are complete. """

        # Print stats for the example tasks
        # example_task_stats = self._get_example_task_stats()
        # print("Number of pages/page types retrieved by test tasks:")
        # print(json.dumps(example_task_stats, indent=4))
        # print()

        # Submit all the tasks in the example tasks
        for example_task in self._get_example_tasks():
            task_input, expected_pages = example_task
            self._submit_task(task_input, expected_pages)
            
        # Validate that all the tasks worked as expected
        self._expect_tasks()
