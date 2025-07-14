from models.Metadata import Metadata, TaskType, Status
from models.ActionInput import InputModel
from models.ActionOutput import OutputModel
from typing import List, Tuple, Union, Dict, Callable, Optional, Set
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from .driver_pool import DriverPool
import threading, time
from errors import TaskNotFoundError

# TODO: Error handling for tasks which don't exist.
# TODO: When a task fails, how do we remove it from the futures.

class TaskManager:
    """
    TaskManager is responsible for managing tasks in the application.
    It provides methods to handle task-related operations such as health checks,
    task management, scraping, cancellation, status checking, result retrieval, and waiting.
    """

    def __init__(self, max_drivers: int = 5, max_workers: int = 5, cleanup_interval: int = 3600):
        # Initailize Driver Pool
        self._max_workers = max_workers
        self._cleanup_interval = cleanup_interval
        self._executer = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, Metadata] = {}
        self._futures: Dict[str, Future] = {}
        self._lock = threading.Lock()

        # Start the cleanup thread
        self._shutdown = False
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_interval,
            daemon=True
        )
        self._cleanup_thread.start()

        # Create the driver pool
        self._max_drivers = max_drivers
        self._driver_pool = DriverPool(max_drivers=max_drivers)

    def _task_exists(self, task_id: str) -> bool:
        """ Check if a task exists """
        with self._lock:
            return self._tasks[task_id] is not None

    def _future_exists(self, task_id: str) -> bool:
        """ Check if a future exists. """
        with self._lock:
            return self._futures[task_id] is not None

    def _task_status(self, task_id: str) -> Status:
        """ Get the hard status of some task. """
        with self._lock:
            task = self._tasks[task_id]
            if task:
                return task.status
            else:
                raise TaskNotFoundError(task_id=task_id)
            
    def _get_all_tasks(self, statuses: Set[Status] = None) -> List[Metadata]:
        """
        Get a list of all tasks.

        Args:
            statuses: Optional set of statuses to filter tasks by.

        Returns:
            List of Metadata objects for all tasks.
        """
        with self._lock:
            if not statuses:
                return list(self._tasks.values())
            return [task for task in self._tasks.values() if task.status in statuses]

    def _cleanup_completed_tasks(self):
        """Background thread to cleanup old completed tasks"""
        while not self._shutdown:
            try:
                time.sleep(self.cleanup_interval)
                current_time = datetime.now()
                
                with self._lock:
                    completed_statuses = {Status.COMPLETED, Status.FAILED, Status.CANCELLED}
                    tasks_to_remove = []
                    
                    for task_id, task in self.tasks.items():
                        if (task.status in completed_statuses and 
                            task.finished_at and 
                            (current_time - task.completed_at).seconds > self.cleanup_interval):
                            tasks_to_remove.append(task_id)
                    
                    for task_id in tasks_to_remove:
                        self.tasks.pop(task_id, None)
                        self.futures.pop(task_id, None)
                        
            except Exception as e:
                print(f"Cleanup thread error: {e}")
                
    def _execute_task(self, task_id: str, func: Callable, args: Tuple = (), kwargs: Dict = {}):
        """Internal method to execute task and update status"""
        try:
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = Status.RUNNING
                    self.tasks[task_id].started_at = datetime.now()
            
            # Execute the function with arguments
            result = func(*args, **kwargs)

            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = Status.COMPLETED
                    self.tasks[task_id].result = result
                    self.tasks[task_id].finished_at = datetime.now()

        except Exception as e:
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = Status.FAILED
                    self.tasks[task_id].error = str(e)
                    self.tasks[task_id].finished_at = datetime.now()

    # This is our worker function...
    def scrape_address(self, task_id: str, address: tuple, pages: list, num_results: int):
        """Worker function to scrape address from property site."""
        with self._lock:
            driver = self._driver_pool.borrow_driver(task_id=, thread_id=)

        # Scrape for the results, hoping there is not error. (TODO: This behavior is inconsistent.)
        results = driver.address_search(address, pages, num_results)

        with self._lock:
            self._driver_pool.return_driver(task_id=, thread_id=, driver=driver)

        # Return the results.
        return results

    def post_scrape_task(self,
                         address: Tuple[int, str, str],
                         pages: List[str],
                         num_results: int
                         ) -> Metadata:
        """
        Create a new scraping task and submit it to the thread pool.

        Args:
            address: Tuple containing number, street, and city.
            pages: List of pages to scrape.
            num_results: Number of results to return from the scrape (1-10).
        """

        # Init new task
        metadata = Metadata(
            address=address,
            pages=pages,
            num_results=num_results
        )
        task_id = metadata.id

        # Update tasks and futures
        with self._lock:
            self._tasks[task_id] = metadata
            
        # kwargs for the worker function.
        kwargs = {
            'task_id': task_id, # Unique task identifier.
            'func': self.scrape_address, # Function to execute in helper worker function/thread.
            'args': (address, pages, num_results), # Arguments to pass to the worker function.
        }

        # Submit the task to the thread pool. 
        # The execute task method will handle the execution and status updates and appropriate states changes and error handling.
        future = self._executer.submit(fn=self._execute_task, **kwargs)
        
        # Update the futures.
        with self._lock:
            self._futures[task_id] = future
            
        # Return the metadata object.
        return metadata


    def get_task_status(self, task_id: str) -> Metadata:
        """ 
        Get the current status and info of a web scraping task.

        Args:
            task_id: Unique task identifier

        Returns:
            Metadata object with details.
        """
        with self._lock:
            task_result = self._tasks.get(task_id)
            if task_result:
                return task_result
        return None

    def get_task_result(self, task_id: str) -> Metadata:
        """ 
        Get the result of a completed task.

        Args:
            task_id: Unique task identifier

        Returns:
            Metadata object with details.
        """
        with self._lock:
            task_result = self._tasks.get(task_id)
            if task_result and task_result.status == Status.COMPLETED:
                return task_result
        return None

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Metadata:
        """
        Wait for a task to complete and return its status.

        Args:
            task_id: Unique task identifier
            timeout: Maximum time to wait in seconds

        Returns:
            Metadata object with final task status or None if timeout/not found
        """
        future = self.futures.get(task_id)
        if not future:
            return None

        try:
            future.result(timeout=timeout)
        except Exception:
            pass  # Exception already handled in _execute_task

        return self.get_task_status(task_id)
