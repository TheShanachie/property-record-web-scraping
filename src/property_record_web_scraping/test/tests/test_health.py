from property_record_web_scraping.test.tests.base_test import BaseAPITest
from property_record_web_scraping.test.test_utilities.logger import test_logger

class TestHealthEndpoint(BaseAPITest):

    def test_health_endpoint(self):
        response = self.client.get_health()
        self.assertValidResponse(response, 200)
        response = response.model_dump()

        # Validate health response structure
        self.assertIn('driver_pool', response)

        # Validate driver pool numbers
        available = response['driver_pool']['num_available']
        active = response['driver_pool']['num_active']
        self.assertIsInstance(available, int)
        self.assertIsInstance(active, int)
        self.assertGreaterEqual(available, 0)
        self.assertGreaterEqual(active, 0)