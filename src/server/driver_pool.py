import threading
import queue
from server.web_scraping_utils.scraper_utils import Driver

class DriverPool:
    def __init__(self, max_drivers=5):
        """Initialize the driver pool with a fixed number of drivers."""
        self.pool = queue.Queue(maxsize=max_drivers)
        self.lock = threading.Lock()

        # Preload the pool with drivers
        for _ in range(max_drivers):
            self.pool.put(self._create_driver())

    def _create_driver(self):
        """Create a new Selenium WebDriver instance."""
        driver = Driver()
        return driver

    def acquire_driver(self):
        """Get a driver from the pool, blocking if none are available."""
        with self.lock:
            return self.pool.get()

    def release_driver(self, driver):
        """Return a driver to the pool."""
        if driver:
            with self.lock:
                try:
                    self.pool.put(driver, block=False)
                except queue.Full:
                    driver.destroy()  # Cleanup if the pool is full

    def shutdown(self):
        """Gracefully close all drivers in the pool."""
        while not self.pool.empty():
            driver = self.pool.get()
            driver.destroy()