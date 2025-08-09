import threading
import queue
from server.web_scraping_utils.scraper_utils import Driver
from typing import Dict, Tuple
from server.logging_utils import resource_management_logger

class DriverPool:
    def __init__(self, max_drivers=5):
        """
            Initialize the driver pool with a fixed number of drivers.
            This pool should provide a thread-safe way to borrow and return drivers.
            
            # TODO: Verify the thread safety of all actions.
        
        """
        self.pool = queue.Queue(maxsize=max_drivers)
        self.lock = threading.RLock()
        self.active_drivers: Dict[str, Driver] = {}

        try: 
            # Preload the pool with drivers
            for _ in range(max_drivers):
                self.pool.put(self._create_driver())
                
            # Log the initialization of the driver pool
            resource_management_logger.info(f"Driver pool initialized with {max_drivers} drivers.")
            
        except Exception as e:
            
            # Log the error if driver pool initialization fails
            resource_management_logger.error("Failed to initialize driver pool.", exc_info=True)
            
            raise RuntimeError("Failed to initialize driver pool.") from e

    def _create_driver(self):
        """ Create a new Selenium WebDriver instance. """
        try:
            # Log the creation of a new driver
            resource_management_logger.info("Creating a new driver instance.")
            
            driver = Driver()
            return driver
        
        except Exception as e:
            
            # Log the error if driver creation fails
            resource_management_logger.error("Failed to create driver.", exc_info=True)
            
            raise RuntimeError("Failed to create driver.") from e
    
    def _available_driver_exists(self) -> bool:
        """ Check whether there exists a non-active driver in the pool. """
        with self.lock:
            return not self.pool.empty()
        
    def _keys(self) -> list:
        """ Get all keys that are used in the active driver mapping. """
        with self.lock:
            return list(self.active_drivers.keys())
        
    def _key_already_used(self, task_id: str) -> bool:
        """ Check whether a key is already used to check out a driver. """
        with self.lock:
            return task_id in self.active_drivers.keys()
        
    def stats(self) -> Dict[str, int]:
        """ 
        Get the stats about the driver pool.
        Included Statistics:
            - Number of available drivers
            - Number of active drivers
            - Driver pool size
        Returns:
            A dictionary with the statistics of the driver pool.
        """
        with self.lock:
            return {
                "num_available": self.pool.qsize(),
                "num_active": len(self.active_drivers),
                "pool_size": self.pool.maxsize,
                "active": {key: value.health() for key, value in self.active_drivers.items()}
            }
        
        
    def borrow_driver(self, task_id: str) -> Driver | None:
        """ 
        Get a driver from the pool, blocking if none are available.
        
        Args: 
            task_id: str that is uuid4 identifier for task.
        
        Returns:
            A Driver object if one is available to be used. Otherwise, returns None
        """
        
        # Check that there is an available driver instance.
        if not self._available_driver_exists():
            resource_management_logger.info("While attempting to borrow a driver: no available drivers in the pool.")
            return None
        
        # Check that the task does not already have a driver. (Or that we havenn't checked one out with the same details.)
        if self._key_already_used(task_id):
            resource_management_logger.info(f"While attempting to borrow a driver: key already in use for task_id: {task_id}.")
            return None
        
        # Update the currrent status of the pool, active tasks, and return
        with self.lock:

            # remove a driver from the pool.
            driver = self.pool.get()
            
            # Add the driver to the active driver mapping
            self.active_drivers[task_id] = driver
            
            # Log the borrowing of the driver
            resource_management_logger.info(f"Driver borrowed for task_id: {task_id}. Active drivers: {len(self.active_drivers)}")
            
            # Return
            return driver
        

    def return_driver(self, task_id: str, raise_error: bool = False):
        """ Return a driver to the pool. """
        
        # Get the driver from the active drivers mapping and remove it.
        with self.lock:
            driver = self.active_drivers.pop(task_id, None)
             
        # Raise an error if the driver does not exist with the given key.
        if not driver:
            if raise_error:
                raise RuntimeError(f"No active driver found for task_id: {task_id}")
            else:
                return
            
        # Log the return of the driver
        resource_management_logger.info(f"While returning driver for task_id: {task_id}, resetting driver.")
            
        # Reset the driver if it exists, and put it back in the pool.
        # TODO: This severely impacts performance. This behavior should be improved.
        driver.reset()
        
        # Then, put the driver back in the pool.
        try:
            # Attempt to put the driver back in the pool.
            with self.lock:
                self.pool.put(driver, block=False)
                
            # Log the successful return of the driver
            resource_management_logger.info(f"Driver returned for task_id: {task_id}. Available drivers: {self.pool.qsize()}")
        
        except queue.Full:
            
            # If the pool is full, destroy the driver.
            driver.destroy()
            
            # Raise an error to indicate that the driver could not be returned.
            if raise_error:
                raise RuntimeError(f"Driver pool is full. Driver for task_id: {task_id} has been destroyed.")


    def kill_driver(self, task_id: str):
        """ 
        Forcefully close a driver and remove it from the pool and active list. 
        This will only kill drivers that are active. If the driver is in the pool, then
        this will do nothing. Even if the driver is being used, then it will be destroyed.
        """
        with self.lock:
            # Remove from active drivers and destroy.
            driver = self.active_drivers.pop(key=task_id, default=None)
            if driver is not None:
                driver.destroy()

    def shutdown(self):
        """ 
        Shutdown the driver pool, destroying all active and non-active drivers.
        This will destroy all drivers in the pool and all active drivers.
        
        # TODO: Verify that this behavior is actually what we want.
        """
        
        # Log the shutdown of the driver pool
        resource_management_logger.info("Shutting down driver pool, destroying all drivers.")
        
        with self.lock:
            # Forcefully destroy any drivers, active or not.
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