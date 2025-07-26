from test.tests.base_test import BaseAPITest
from test.test_utilities.logger import test_logger

class TestHealthEndpoint(BaseAPITest):

    def test_health_endpoint(self):
        response = self.client.get_health()
        self.assertValidResponse(response, 200)

        # Validate health response structure
        self.assertIn('driver_pool', response.metadata)
        self.assertIn('available', response.metadata['driver_pool'])
        self.assertIn('active', response.metadata['driver_pool'])

        # Validate driver pool numbers
        available = response.metadata['driver_pool']['available']
        active = response.metadata['driver_pool']['active']
        self.assertIsInstance(available, int)
        self.assertIsInstance(active, int)
        self.assertGreaterEqual(available, 0)
        self.assertGreaterEqual(active, 0)