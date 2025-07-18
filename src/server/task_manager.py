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
            self._futures: Dict[str, (Future, threading.Event)] = {}
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
        # TODO: No good. This needs to be modeled after the class is fixed.
        """
        pass

    def _task_exists(self, task_id: str) -> bool:
        """ Check if a task exists """
        with self._lock:
            return self._tasks[task_id] is not None

    def _future_exists(self, task_id: str) -> bool:
        """ Check if a future exists. """
        with self._lock:
            return self._futures[task_id][0] is not None
        
    def _future_finished_with_error(self, task_id: str) -> bool:
        """ Check if a future has finished with an error. """
        with self._lock:
            future = self._futures.get(task_id)[0]
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
                raise RuntimeError(f"Task with ID '{task_id}' does not exist.")
            
    def _task_id_of_future(self, future: Future) -> Optional[str]:
        """ 
        Get the task_id of a created future. 
        """
        with self._lock:
            for task_id, (fut, _) in self._futures.items():
                if fut == future:
                    return task_id
            return None
        
    def _cancel_task(self, task_id: str):
        """ 
        Cancel a task and perform appropriate state changes. This function does not immediatly stop a task. Instead, it 
        performs state changes so the task begins to end early as soon as it can. This method does not raise assertion errors.
        Instead it raises a Runtime error if any of the assertions or behavior does not work as expected. There are several 
        possible scenarios for this behavior as follows:
        
        1. The task has not started yet, so it can be cancelled immediately with default threading functionality.
        2. The task is running, so we set a quit event and change the status. Then the task will end early, but still take time.
        3. The task is already finished, so we do nothing. (Make some assertions about the state of relevant data.)
            
        Args:
            task_id: Unique identifier for the task to be cancelled.
            
        Raises:
            RuntimeError: If there is an error attempting to cancel this task.
        """
        try: # Attempt to cancel the task.
            with self._lock:
                # Get relevant task data assert that the data exists.
                task = self._tasks.get(task_id, None) # Get the task data.
                future_data = self._futures.get(task_id, None) # Get the future data.
        
                # The must be included in our mappings.
                assert task is not None, f"Task with ID '{task_id}' does not exist." 
                
                # Check that the task is in a finished state.
                if task.status in {Status.COMPLETED, Status.FAILED, Status.CANCELLED}:
                    return  # Task is already finished, nothing to cancel.
                
                # If the task is already stopping, then we do nothing besides asserting the state.
                if task.status == Status.STOPPING:
                    assert future_data is not None, f"Future data for task_id '{task_id}' is missing while task is stopping."
                    assert future_data[1].is_set(), f"Quit event for task_id '{task_id}' is not set while task is stopping."
                    return
                
                # At this point, the task is running so there must be a future and quit event.
                assert future_data is not None, f"Future data for task_id '{task_id}' is missing while task is running."
                
                # If the future is not running, then we can try to cancel it.
                future, quit_event = future_data
                
                # If the future is already done, then we do nothing.
                if future.done():
                    return
                
                # If the future is not done, then we can try to cancel it.
                if future.cancel():  # Attempt to cancel the future.
                    return
                
                # If the future could not be cancelled, then we resort to setting the quit event and waiting for it to finish early.
                quit_event.set()  # Signal the task to stop if it is running
                task.status = Status.STOPPING  # Update the task status to stopping
                
                return  # Task cancellation initiated, but may take time to complete.
            
        except Exception as e:
            
            # If there is an error, we raise a RuntimeError with the error message.
            raise RuntimeError(f"Error while attempting to cancel task with ID '{task_id}': {e}")
                
                
    def _task_finished_callback_wrapper(self) -> Callable[[Future], None]:
        """ 
        Wrapper for the task finished callback to create a closure, insuring that the parent object data is accessible.     
        
        Returns:
            A callback function that can be used with futures to handle task completion.
        """
        
        # Create functions in this closure for the possible ending actions of a task.
        def _finish_successfully(future: Future, task_id: str) -> None:
            """
            Handle the case where a task finished successfully. This method assumes that
            the future has finished correctly, without errors and the result is available.
            Assertions are made to ensure these conditions are met.
            
            Args:
                future: The Future object representing the completed task.
                task_id: The unique identifier for the task.
                
            Raises:
                AssertionError: If the future is not done, if the task_id or task metadata cannot be found, or the task did not finish successfully w/o errors.
            """
            assert future.done(), "Future is not done. Something went wrong."
            assert future.result() is not None, "Future did not finish with a result."
            
            # Get the task metadata object.
            with self._lock:
                task_metadata = self._tasks.get(task_id, None)
                assert task_metadata is not None, f"Task metadata not found for task_id: {task_id}."
                
                # With this task metadata, we can update the status and result.
                task_metadata.status = Status.COMPLETED
                task_metadata.result = future.result()
                task_metadata.finished_at = datetime.now()
        
        def _finish_with_error(future: Future, task_id: str) -> None:
            """
            Handle the case where a task finished with an error. This method assumes that
            the future has finished with an exception and the result is not available.
            
            Args:
                future: The Future object representing the completed task.
                task_id: The unique identifier for the task.
                
            Raises:
                AssertionError: If the future is not done, if the task_id or task metadata cannot be found, or the task did not finish with an error.
            """
            assert future.done(), "Future is not done. Something went wrong."
            assert future.exception() is not None, "Future did not finish with an exception."
            
            # Get the task metadata object.
            with self._lock:
                task_metadata = self._tasks.get(task_id, None)
                assert task_metadata is not None, f"Task metadata not found for task_id: {task_id}."
            
                # With this task metadata, we can update the status and error.
                task_metadata.status = Status.FAILED
                task_metadata.error = future.exception()
                task_metadata.finished_at = datetime.now()
        
        def _finish_with_quit(future: Future, task_id: str) -> None:
            """
            Handle the case where a task finished due to a quit event. This method assumes that
            the future has finished early due to a quit event and the result is available. 
            
            Args:
                future: The Future object representing the completed task.
                task_id: The unique identifier for the task.
                
            Raises:
                AssertionError: If the future is not done, if the task_id or task metadata cannot be found, or the task did not finish with a quit event.
            """
            assert future.done(), "Future is not done. Something went wrong."
            assert future.result() is not None, "Future did not finish with a result."
            
            # Get the task metadata object.
            with self._lock:
                # Is the quit event set?
                future_data = self._futures.get(task_id, None)
                assert future_data and future_data[1].is_set(), f"Quit event is not set for task_id: {task_id}."
                
                # Get the task metadata object.
                task_metadata = self._tasks.get(task_id, None)
                assert task_metadata is not None, f"Task metadata not found for task_id: {task_id}."
                                
                # With this task metadata, we can update the status and result.
                task_metadata.status = Status.CANCELLED
                task_metadata.result = future.result() # We expect this to be at least an empty list.
                task_metadata.finished_at = datetime.now()
        
        def _finish_with_cancelled(future: Future, task_id: str) -> None:
            """
            Handle the case where a task was cancelled before running. This method assumes that
            the future was cancelled and no result is available.
            
            Args:
                future: The Future object representing the completed task.
                task_id: The unique identifier for the task.
                
            Raises:
                AssertionError: If the future is not done, if the task_id or task metadata cannot be found, or the task was not cancelled.
            """
            assert future.done(), "Future is not done. Something went wrong."
            assert future.cancelled(), "Future was not cancelled before running."
            
            # Get the task metadata object.
            with self._lock:
                task_metadata = self._tasks.get(task_id, None)
                assert task_metadata is not None, f"Task metadata not found for task_id: {task_id}."
                
                # With this task metadata, we can update the status.
                task_metadata.status = Status.CANCELLED
                task_metadata.finished_at = datetime.now()
        
        # Define the callback function that will be called when a task is finished.
        def _task_finished_callback(future: Future) -> None:
            """
            Callback function to handle task completion. This method makes some 
            assertions based on expected behavior. We assume the future is done,
            the future and corresponding metadata object are available and mapped
            to a unique task_id. Assertion errors will be raised if these
            conditions are not met.
            
            There are several possible outcomes for a finished future:
            1. The future was cancelled before running. (no result)
            2. The future completed successfully. (result is available)
            3. The future completed with an exception. (no result)
            4. The future completed early due to a quit/cancel event. (result is available)
            Args:
                future: The Future object representing the completed task.
                
            Raises:
                AssertionError: If the future is not done, or if the task_id or task metadata cannot be found.
            """
            
            # Since this is a future callback, we can assume the task is done.
            assert future.done(), "Future is not done. Something went wrong."
            
            # Get the task_id from the future.
            task_id = self._task_id_of_future(future)
            assert task_id is not None, "Task ID not found for the completed future."
            
            # Get the task metadata object.
            with self._lock:
                task_metadata = self._tasks.get(task_id, None)
                assert task_metadata is not None, f"Task metadata not found for task_id: {task_id}."
            
                # Address the possible outcomes for the task.
                
                # 1. The future was cancelled before running. (no result)
                if future.cancelled(): # The future was cancelled before running.
                   _finish_with_cancelled(future, task_id)
                   return
               
                # 2. The future completed with an exception. (no result)
                if future.exception() is not None: # The future completed with an exception.
                    _finish_with_error(future, task_id)
                    return
                
                # 3. The future completed early due to a quit/cancel event. (result is available)
                if future.done() and self._futures.get(task_id, None)[1].is_set():
                    _finish_with_quit(future, task_id)
                    return
               
                # 4. The future completed successfully. (result is available)
                if future.result() is not None:
                    _finish_successfully(future, task_id)
                    return
                
            # If none of the conditions were met, we raise an error. Something went wrong.
            raise RuntimeError(f"Task with ID '{task_id}' finished in an unexpected state.")
                    
            ## THIS IS THE END OF THE CALLBACK FUNCTION ##
            ## IM BLIND AND STUPID SO I NEED THIS LOL ##
        
        # Return the callback function which we just defined.        
        return _task_finished_callback
        
             

    def _cleanup_completed_tasks(self) -> None:
        """ Background thread to cleanup old completed tasks """
        # TODO: There's a very good chance this function is trash
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
        
    # TODO: Refactor the scraping methodology! We do not need this many layers, especially with the driver pool and callbacks. Look into how to reorder the state changes in the metadata

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
                       num_results: int, quit_event: threading.Event = None)  -> Union[list,  None]:
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
                driver = None
                while driver is None:
                    driver = self._driver_pool.borrow_driver(
                    task_id=task_id, thread_id=thread_id)
                    time.sleep(10)

            # Scrape for the results, hoping there is not error. (TODO: This behavior is inconsistent.)
            results = driver.address_search(address, pages, num_results, quit_event)

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
                    if 'results' in locals():
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
                
            # Create quit event for task
            quit_event = threading.Event()
                
            # kwargs for the worker function.
            kwargs = {
                'task_id': task_id,  # Unique task identifier.
                # Function to execute in helper worker function/thread.
                'func': self.scrape_address,
                # Arguments to pass to the worker function.
                'args': (task_id, address, pages, num_results, quit_event),
            }

            # Submit the task to the thread pool.
            # The execute task method will handle the execution and status updates and appropriate states changes and error handling.
            future = self._executer.submit(self._execute_task, **kwargs)

            # Update the futures.
            with self._lock:
                self._futures[task_id] = (future, quit_event)

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

    def get_task_status(self, task_id: str) -> Metadata:
        """
        Get the current status and info of a web scraping task.

        Args:
            task_id: Unique task identifier

        Returns:
            Metadata object with details.
            
        Raises:
            RuntimeError: If the task_id does not exist or if the task is not found.
        """
        
        with self._lock:
            task_result = self._tasks.get(task_id, None)
            if not task_result: 
                raise RuntimeError(f"No task was found for task_id: {task_id}")
            return task_result

    def get_task_result(self, task_id: str) -> Metadata | None:
        """
        Get the result of a completed task.

        Args:
            task_id: Unique task identifier

        Returns:
            Metadata object with details or None if the task is not completed or does not exist.
        """
        with self._lock:            
            task_result = self._tasks.get(task_id)
            if task_result and task_result.status in {Status.COMPLETED, Status.CANCELLED, Status.FAILED}:
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
            
        # TODO: This should absolutly not exist as part of the TaskManager. Refactor when appropriate.
        """
        future = None
        with self._lock:
            future = self._futures.get(task_id)[0]
            if future and future.done() and future.exception() is not None:
                raise future.exception()
            
        if not future:
            return None

        try:
            future.result(timeout=timeout)
        except Exception:
            pass  # Exception already handled in _execute_task

        return self.get_task_status(task_id)
