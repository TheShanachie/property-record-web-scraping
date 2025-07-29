from test.tests.base_test import BaseAPITest
from test.test_utilities.logger import test_logger

class TestTaskListEndpoint(BaseAPITest):

    def test_tasks_endpoint(self):
        response = self.client.get_tasks()
        self.assertValidResponse(response, expected_status=200)