import threading
import queue
from server.web_scraping_utils.scraper_utils import Driver
from typing import Dict, Tuple

class DriverPool:
    def __init__(self, max_drivers=5):
        """Initialize the driver pool with a fixed number of drivers."""
        self.pool = queue.Queue(maxsize=max_drivers)
        self.lock = threading.Lock()
        self.active_drivers: Dict[Tuple[str, str], Driver] = {}

        # Preload the pool with drivers
        for _ in range(max_drivers):
            self.pool.put(self._create_driver())

    def _create_driver(self):
        """Create a new Selenium WebDriver instance."""
        driver = Driver()
        return driver
    
    def _available_driver_exists(self) -> bool:
        """ Check whether there exists a non-active driver in the pool. """
        with self.lock:
            return len(self.pool) > 0
        
    def _key_already_used(self, task_id: str, thread_id: str) -> bool:
        """ Check whether a key is already used to check out a driver. """
        with self.lock:
            try: 
                return self.active_drivers[(task_id, thread_id)] is not None
            except:
                return False
        
        
    def borrow_driver(self, task_id: str, thread_id: str) -> Driver | None:
        """ 
        Get a driver from the pool, blocking if none are available.
        
        Args: 
            task_id: str that is uuid4 identifier for task.
            thread_id: id given by 'threading.get_ident' function. (The function should be called and the id should be passed as an argument.)
        
        Returns:
            A Driver object if one is available to be used. Otherwise, returns None
        """
        
        # Check that there is an available driver instance.
        if not self._available_driver_exists():
            return None
        
        # Check that the task does not already have a driver. (Or that we havenn't checked one out with the same details.)
        if self._key_already_used(task_id, thread_id):
            return None
        
        # Update the currrent status of the pool, active tasks, and return
        with self.lock:
            
            # Create new id key for active pool.
            key = (task_id, thread_id)

            # remove a driver from the pool.
            driver = self.pool.get()
            
            # Add the driver to the active driver mapping
            self.active_drivers[key] = driver
            
            # Return
            return driver
        

    def return_driver(self, task_id: str, thread_id: str, driver: Driver) -> None:
        """ Return a driver to the pool. """
        
        # Reset the driver.
        # TODO: This severely impacts performance. This behavior should be improved.
        driver.reset()
                
        if driver:
            with self.lock:
                
                try:
                    # Remove from active drivers
                    self.active_drivers.pop(key=(task_id, thread_id))
                    
                    # Put the driver back
                    self.pool.put(driver, block=False)
                    
                except queue.Full:
                    driver.destroy()  # Cleanup if the pool is full


    def kill_driver(self, task_id: str, thread_id: str):
        """ 
        Forcefully close a driver and remove it from the pool and active list. 
        This will only kill drivers that are active. If the driver is in the pool, then
        this will do nothing.
        """
        with self.lock:
            # Remove from active drivers and destroy.
            driver = self.active_drivers.pop(key=(task_id, thread_id), default = None)
            if driver is not None:
                driver.destroy()

    def shutdown(self):
        """ Gracefully close all drivers in the pool and kill any drivers which are active. """
        with self.lock:
            # Forcefully destroy any active drivers.
            values = self.active_drivers.values()
            self.active_drivers.clear()
            while values:
                driver = values[-1]
                driver.destroy()
                values = values[:-1]
                
        # Destroy non-active drivers.
        while not self.pool.empty():
            driver = self.pool.get()
            driver.destroy()