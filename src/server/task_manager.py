from .models.Metadata import Metadata, TaskType, Status
from .models.ActionInput import InputModel
from .models.ActionOutput import OutputModel
from typing import List, Tuple, Union, Dict, Callable, Optional, Set
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from .driver_pool import DriverPool
import threading
import time
from .errors import TaskNotFoundError

# TODO: Error handling for tasks which don't exist.
# TODO: When a task fails, how do we remove it from the futures.


class TaskManager:
    """
    TaskManager is responsible for managing tasks in the application. It provides methods to handle task-related operations such as health checks, task management, scraping, cancellation, status checking, result retrieval, and waiting.
    """

    def __init__(self, max_drivers: int = 5, max_workers: int = 5, cleanup_interval: int = 3600):

        try:
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
                target=self._cleanup_completed_tasks,
                daemon=True
            )
            self._cleanup_thread.start()

            # Create the driver pool
            self._max_drivers = max_drivers
            self._driver_pool = DriverPool(max_drivers=max_drivers)

        except Exception as e:

            # Simply raise the error to the next scope.
            raise RuntimeError(f"Failed to initialize TaskManager: {e}")
        
    def shutdown(self):
        """
        Shutdown the TaskManager, cleaning up resources and stopping the cleanup thread.
        """
        self._shutdown = True
        self._cleanup_thread.join()
        self._executer.shutdown(wait=True)
        self._driver_pool.shutdown()

    def _task_exists(self, task_id: str) -> bool:
        """ Check if a task exists """
        with self._lock:
            return self._tasks[task_id] is not None

    def _future_exists(self, task_id: str) -> bool:
        """ Check if a future exists. """
        with self._lock:
            return self._futures[task_id] is not None
        
    def _future_finished_with_error(self, task_id: str) -> bool:
        """ Check if a future has finished with an error. """
        with self._lock:
            future = self._futures.get(task_id)
            if future:
                return future.done() and future.exception() is not None
            return False

    def _task_status(self, task_id: str) -> Status:
        """ Get the hard status of some task. """
        with self._lock:
            task = self._tasks[task_id]
            if task:
                return task.status
            else:
                raise TaskNotFoundError(task_id=task_id)
    def get_all_tasks(self, statuses: Set[Status] = None) -> List[Metadata]:
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

    def _cleanup_completed_tasks(self) -> None:
        """ Background thread to cleanup old completed tasks """
        while not self._shutdown:
            try:
                time.sleep(self._cleanup_interval)
                current_time = datetime.now()

                with self._lock:
                    completed_statuses = {Status.COMPLETED,
                                          Status.FAILED, Status.CANCELLED}
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

                # Simply raise the error to the next scope.
                raise RuntimeError(f"Error during cleanup: {e}")

    def _execute_task(
            self, task_id: str, func: Callable, args: Tuple = (),
            kwargs: Dict = {}) -> None:
        """ Internal method to execute task and update status """
        try:
            with self._lock:
                if task_id in self._tasks.keys():
                    self._tasks[task_id].status = Status.RUNNING
                    self._tasks[task_id].started_at = datetime.now()
                    
            # Execute the function with arguments
            result = func(*args, **kwargs)

            with self._lock:
                if task_id in self._tasks.keys():
                    self._tasks[task_id].status = Status.COMPLETED
                    self._tasks[task_id].result = result
                    self._tasks[task_id].finished_at = datetime.now()

        except Exception as e:
            with self._lock:
                if task_id in self._tasks.keys():
                    self._tasks[task_id].status = Status.FAILED
                    self._tasks[task_id].error = e
                    if 'result' in locals():
                        self._tasks[task_id].result = result
                    self._tasks[task_id].finished_at = datetime.now()

    # This is our worker function...
    def scrape_address(self, task_id: str, address: tuple, pages: list,
                       num_results: int) -> Union[List[Dict],
                                                  None]:
        """
        Worker function to scrape address from property site. In all cases,
        whether the task succeeds or fails, this method will ensure that the
        driver is returned to the pool.
        """

        try:
            # Get the id of the thread that is executing this task.
            thread_id = threading.get_ident()

            # check out a driver from the pool.
            with self._lock:
                driver = self._driver_pool.borrow_driver(
                    task_id=task_id, thread_id=thread_id)

            # Scrape for the results, hoping there is not error. (TODO: This behavior is inconsistent.)
            results = driver.address_search(address, pages, num_results)

            with self._lock:
                self._driver_pool.return_driver(
                    task_id=task_id, thread_id=thread_id)

            # Return the results.
            return results

        except Exception as e:
            with self._lock:

                # Return the driver to the pool if there is an error, if there is a driver that is checked out.
                self._driver_pool.return_driver(
                    task_id=task_id, thread_id=thread_id, raise_error=False)

                # If there is an error, we need to return the driver to the pool.
                if task_id in self._tasks:
                    self._tasks[task_id].status = Status.FAILED
                    self._tasks[task_id].error = e
                    self.tasks[task_id].result = results
                    self._tasks[task_id].finished_at = datetime.now()

    def post_scrape_task(self,
                         address: Tuple[int, str, str],
                         pages: List[str],
                         num_results: int
                         ) -> Metadata:
        """
        Create a new scraping task and submit it to the thread pool.
        This method is needlessly complicated, but it allows to keep
        track of certain metadata and state changes.
        Args:
            address: Tuple containing number, street, and city.
            pages: List of pages to scrape.
            num_results: Number of results to return from the scrape (1-10).
        """
        try:

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
                'task_id': task_id,  # Unique task identifier.
                # Function to execute in helper worker function/thread.
                'func': self.scrape_address,
                # Arguments to pass to the worker function.
                'args': (task_id, address, pages, num_results),
            }

            # Submit the task to the thread pool.
            # The execute task method will handle the execution and status updates and appropriate states changes and error handling.
            future = self._executer.submit(self._execute_task, **kwargs)

            # Update the futures.
            with self._lock:
                self._futures[task_id] = future

            # Return the metadata object.
            return metadata

        except Exception as e:

            # If a task id is created at this point, get it.
            if 'task_id' in locals():
                with self._lock:
                    self._tasks.pop(task_id, None)
                    self._futures.pop(task_id, None)

            # Raise the error to the next scope.
            raise RuntimeError(f"Failed to post scrape task: {e}")

    def get_task_status(self, task_id: str) -> Metadata | None:
        """
        Get the current status and info of a web scraping task.

        Args:
            task_id: Unique task identifier

        Returns:
            Metadata object with details.
        """
        with self._lock:
            future = self._futures.get(task_id)
            if future and future.done() and future.exception() is not None:
                raise future.exception()
            
            task_result = self._tasks.get(task_id)
            if task_result:
                return task_result
        return None

    def get_task_result(self, task_id: str) -> Metadata | None:
        """
        Get the result of a completed task.

        Args:
            task_id: Unique task identifier

        Returns:
            Metadata object with details.
        """
        with self._lock:
            future = self._futures.get(task_id)
            if future and future.done() and future.exception() is not None:
                raise future.exception()
            
            task_result = self._tasks.get(task_id)
            if task_result and task_result.status == Status.COMPLETED:
                return task_result
        return None

    def wait_for_task(
            self, task_id: str, timeout: float = 60) -> Metadata | None:
        """
        Wait for a task to complete and return its status.
        
        # TODO: This method does not achieve the required behavior at all.

        Args:
            task_id: Unique task identifier
            timeout: Maximum time to wait in seconds

        Returns:
            Metadata object with final task status or None if timeout/not found
        """
        future = None
        with self._lock:
            future = self._futures.get(task_id)
            if future and future.done() and future.exception() is not None:
                raise future.exception()
            
        if not future:
            return None

        try:
            future.result(timeout=timeout)
        except Exception:
            pass  # Exception already handled in _execute_task

        return self.get_task_status(task_id)
