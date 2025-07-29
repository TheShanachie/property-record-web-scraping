from server.models.Metadata import Metadata, TaskType, Status
from server.models.ActionInput import InputModel
from server.models.ActionOutput import OutputModel
from typing import List, Tuple, Union, Dict, Callable, Optional, Set
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from server.driver_pool import DriverPool
from server.logging_utils import event_handling_operations_logger
import threading
import time, json

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
            self._lock = threading.RLock()  # Use RLock to allow reentrant locking

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
            
            # Log the initialization of the TaskManager
            event_handling_operations_logger.debug(
                f"TaskManager initialized with max_workers={max_workers}, max_drivers={max_drivers}, cleanup_interval={cleanup_interval} seconds."
            )

        except Exception as e:
            
            # Log the error during initialization
            event_handling_operations_logger.error(
                f"Error initializing TaskManager: {e}", exc_info=True)

            # Simply raise the error to the next scope.
            raise RuntimeError(f"Failed to initialize TaskManager: {e}") from e
        
    def driver_pool_info(self) -> dict:
        """
        Get information about the driver pool.
        
        Returns:
            A dictionary containing the driver pool information.
        """
        return self._driver_pool.stats()
        
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
                    
                    # Log this event
                    event_handling_operations_logger.debug(
                        f"Attempted to cancel task with ID '{task_id}' that is already finished."
                    )
                    
                    return  # Task is already finished, nothing to cancel.
                
                # If the task is already stopping, then we do nothing besides asserting the state.
                if task.status == Status.STOPPING:
                    assert future_data is not None, f"Future data for task_id '{task_id}' is missing while task is stopping."
                    assert future_data[1].is_set(), f"Quit event for task_id '{task_id}' is not set while task is stopping."
                    
                    # Log this event
                    event_handling_operations_logger.debug(
                        f"While attempting to cancel task, task with ID '{task_id}' is already stopping, no further action needed."
                    )
                    
                    return
                
                # At this point, the task is running so there must be a future and quit event.
                assert future_data is not None, f"Future data for task_id '{task_id}' is missing while task is running."
                
                # If the future is not running, then we can try to cancel it.
                future, quit_event = future_data
                
                # If the future is already done, then we do nothing.
                if future.done():
                    
                    # Log this event
                    event_handling_operations_logger.debug(
                        f"Attempted to cancel task with ID '{task_id}' that is already done."
                    )
                    
                    return
                
                # If the future is not done, then we can try to cancel it.
                if future.cancel():  # Attempt to cancel the future.
                    
                    # Log the cancellation event.
                    event_handling_operations_logger.debug(
                        f"Task with ID '{task_id}' was cancelled successfully via threading functionality."
                    )
                    
                    return
                
                # If the future could not be cancelled, then we resort to setting the quit event and waiting for it to finish early.
                quit_event.set()  # Signal the task to stop if it is running
                task.status = Status.STOPPING  # Update the task status to stopping
                
                # Log the cancellation event.
                event_handling_operations_logger.debug()
                
                # Log the cancelation event
                event_handling_operations_logger.debug(
                    f"Task with ID '{task_id}' could not be cancelled immediately, but quit event is set and task is stopping."
                )
                
                return  # Task cancellation initiated, but may take time to complete.
            
        except Exception as e:
            
            # Log the error during task cancellation
            event_handling_operations_logger.error(
                f"Error while attempting to cancel task with ID '{task_id}': {e}", exc_info=True
            )
            
            # If there is an error, we raise a RuntimeError with the error message.
            raise RuntimeError(f"Error while attempting to cancel task with ID '{task_id}': {e}")
                
                
    def _get_task_finished_callback(self) -> Callable[[Future], None]:
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
            
            # Get the task metadata object.
            with self._lock:
                task_metadata = self._tasks.get(task_id, None)
                assert task_metadata is not None, f"Task metadata not found for task_id: {task_id}."
                
                # With this task metadata, we can update the status and result.
                task_metadata.status = Status.COMPLETED
                task_metadata.result = future.result()
                task_metadata.finished_at = datetime.now()
                
                # Log the successful completion of the task.
                event_handling_operations_logger.debug(
                    f"Task with ID '{task_id}' completed successfully with result: {task_metadata.result.__sizeof__() if task_metadata.result else 'None'} bytes."
                )
        
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
                
                # Log the error that occurred during task completion.
                event_handling_operations_logger.debug(
                    f"Task with ID '{task_id}' finished healthfully, but failed before completion with error: {task_metadata.error}."
                )
        
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
                
                # Log the quit event that occurred during task completion.
                event_handling_operations_logger.debug(
                    f"Task with ID '{task_id}' finished early due to a quit event with result: {task_metadata.result.__sizeof__() if task_metadata.result else 'None'} bytes."
                )
        
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
                
                # Log the cancellation event.
                event_handling_operations_logger.debug(
                    f"Task with ID '{task_id}' was cancelled before running."
                )
                
        def _verify_driver_is_returned(task_id: str) -> None:
            """
            Verify that the driver is returned to the pool after task completion.
            This method checks if the driver associated with the task_id is returned
            to the pool and raises an assertion error if it is not.
            
            Args:
                task_id: The unique identifier for the task.
                
            Raises:
                AssertionError: If the driver is not returned to the pool.
            """
            
            # TODO: Implement this method to verify that the driver is returned to the pool.
            in_use = self._driver_pool._key_already_used(task_id)
            assert not in_use, f"Driver for task_id '{task_id}' exists in the active drivers mapping, but should have been returned to the pool."
            
        
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
            
            # Log the use of the callback function.
            event_handling_operations_logger.debug(f"Callback function is being called.")
            
            try:
            
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
                        
                        # Log the behavior.
                        event_handling_operations_logger.debug(
                            f"Callback finalizing for task with ID '{task_id}'. The future was cancelled before running."
                        )
                        
                    # 2. The future completed with an exception. (no result)
                    elif future.exception() is not None: # The future completed with an exception.
                        _finish_with_error(future, task_id)
                        
                        # Log the behavior.
                        event_handling_operations_logger.debug(
                            f"Callback finalizing for task with ID '{task_id}'. The future completed with an exception: {future.exception()}"
                        )
                        
                    # 3. The future completed early due to a quit/cancel event. (result is available)
                    elif future.done() and self._futures.get(task_id, None)[1].is_set():
                        _finish_with_quit(future, task_id)
                        
                        # Log the behavior.
                        event_handling_operations_logger.debug(
                            f"Callback finalizing for task with ID '{task_id}'. The future completed early due to a quit event with result: {task_metadata.result.__sizeof__() if task_metadata.result else 'None'} bytes."
                        )
                        
                    # 4. The future completed successfully. (result is available)
                    else:
                        _finish_successfully(future, task_id)
                        
                        # Log the behavior.
                        event_handling_operations_logger.debug(
                            f"Callback finalizing for task with ID '{task_id}'. The future completed successfully."
                        )
                
                # Verify driver is returned OUTSIDE the lock to prevent deadlock
                _verify_driver_is_returned(task_id)
                return
                    
            # Handle a number of errors. (Log these errors.)
            except Exception as e:
                
                # Log the error that occurred during task completion.
                event_handling_operations_logger.error(
                    f"Error while finalizing task with ID '{task_id}': {e}", exc_info=True
                )
                
                # If there is an error, we raise a RuntimeError with the error message.
                raise RuntimeError(f"Error while finalizing task with ID '{task_id}': {e}") from e
                    
            ## THIS IS THE END OF THE CALLBACK FUNCTION ##
            ## IM BLIND AND STUPID SO I NEED THIS INDICATION LOL ##
        
        # Return the callback function which we just defined.        
        return _task_finished_callback
        
             

    def _cleanup_completed_tasks(self) -> None:
        """ Background thread to cleanup old completed tasks """
        # TODO: There's a very good chance this function is trash
        # TODO: THIS FUNCTION IS TRASH, IT NEEDS TO BE REFACTORED.
        pass
            
                
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

    # def _execute_task(
    #         self, task_id: str, func: Callable, args: Tuple = (),
    #         kwargs: Dict = {}) -> None:
    #     """ Internal method to execute task and update status """
    #     try:
    #         with self._lock:
    #             if task_id in self._tasks.keys():
    #                 self._tasks[task_id].status = Status.RUNNING
    #                 self._tasks[task_id].started_at = datetime.now()
                    
    #         # Execute the function with arguments
    #         result = func(*args, **kwargs)

    #         with self._lock:
    #             if task_id in self._tasks.keys():
    #                 self._tasks[task_id].status = Status.COMPLETED
    #                 self._tasks[task_id].result = result
    #                 self._tasks[task_id].finished_at = datetime.now()

    #     except Exception as e:
    #         with self._lock:
    #             if task_id in self._tasks.keys():
    #                 self._tasks[task_id].status = Status.FAILED
    #                 self._tasks[task_id].error = e
    #                 if 'result' in locals():
    #                     self._tasks[task_id].result = result
    #                 self._tasks[task_id].finished_at = datetime.now()
    
    def _poll_for_driver(self, task_id: str, interval: int = 10, timeout: int | None = None):
        """
        Poll for a driver to become available in the pool. The interval must be smaller than the timeout if one is specified.
        
        Args:
            task_id: Unique identifier for the task.
            interval: Time in seconds to wait between polls.
            timeout: Optional maximum time in seconds to wait for a driver.
            
        Returns:
            A driver from the pool when available.
            
        Raises:
            RuntimeError: If no driver is available within the timeout period.
            AssertionError: If the interval is not greater than 0 or if the timeout is not greater than the interval.
        """
        
        # Assert basic conditions 
        assert interval > 0, "Interval must be greater than 0."
        assert timeout is None or timeout > interval, "Timeout must be greater than interval if specified."
        
        # Log the behavior here.
        event_handling_operations_logger.debug(f"Starting to poll for driver for task: {task_id} and interval: {interval}.")
        
        # Start time for timeout (This is a float so not pretty)
        end_time = time.time() + timeout if timeout else None
        
        while True:
            
            # Attempt to borrow a driver.
            driver = self._driver_pool.borrow_driver(task_id=task_id)
            
            # If the driver is not None, return the driver.
            if driver:
                event_handling_operations_logger.debug(f"While polling for driver for task: {task_id}, driver was found.")
                return driver
            
            # Do we wait anymore or is there a timeout
            if timeout and (end_time < time.time()):
                raise RuntimeError(f"While polling for a driver from the driver pool, a timeout occured after {timeout} seconds.")
            
            # Log this behavior
            event_handling_operations_logger.debug(f"While polling for driver for task: {task_id}, none was found. Waiting interval: {interval}")
            
            # Otherwise, we wait and poll again if appropriate.
            time.sleep(interval)
        
        
                    
    def _execute_scrape_task(self, task_id: str, quit_event: threading.Event) -> List | None:
        """
        Internal method to execute a scraping task and update its status. This method is used to execute the scrape task and go through the 
        motions which should be performed in a separate thread. This method does not update the metadata of a task, besides the task start
        time. All other metadata updates are performed by the callback function which is defined in the parent class. This method will return
        the results of the scrape task, which will be updated in the metadata object by the callback function. If any errors occur through
        this process, a RuntimeError will be raised with the error message and available data.        
        
        Args:
            task_id: Unique identifier for the task.
            
        Returns:
            List of results from the scrape task or None if no results are found.
            
        Raises:
            RuntimeError: If any errors occur during the execution of this method.

        """
        
        # Try to execute the scrape task actions
        try:
            
            # Get the data for the task, i.e. the address, pages, results, quit event, etc.
            with self._lock:
                task_data = self._tasks.get(task_id, None)
                if not task_data:
                    raise RuntimeError(f"Task with ID '{task_id}' does not exist. Could not execute the scrape task.")
                
                # Update the task status to running.
                task_data.status = Status.RUNNING
                task_data.started_at = datetime.now()
            
            # Get a driver from the pool and execute the scrape_address function.
            driver = self._poll_for_driver(task_id=task_id,
                                           interval=10,
                                           timeout=None)
                
            # Once we have a driver, we can execute the scrape_address function.
            results = driver.address_search(
                address=task_data.address,
                pages=task_data.pages,
                num_results=task_data.num_results,
                quit_event=quit_event
            )
            
            # After the scrape is complete, we need to return the driver to the pool.
            self._driver_pool.return_driver(task_id=task_id)
            
            # Log the successful execution of the scrape task.
            event_handling_operations_logger.debug(
                f"Scrape task with ID '{task_id}' executed successfully with {results.__sizeof__() if results else 'None'} bytes of results. Results: {results}."
            )
            
            # Return the results.
            return results
        
        except Exception as e:
            
            # Log the error
            event_handling_operations_logger.error(
                f"Error while executing scrape task with ID '{task_id}': {e}", exc_info=True
            )
            
            # Some error occurred during the execution of the scrape task.
            raise RuntimeError(f"Error while executing scrape task with ID '{task_id}': {e}") from e
        
    def post_scrape_task(self, address: Tuple[int, str, str], pages: List[str], num_results: int) -> Metadata:
        """
            This method creates a new scraping task and submits it to the thread pool. It initializes the task metadata, updates the tasks and futures mappings, and submits the task to the thread pool for execution.
        
        """
        
        # Create a new metadata object for the task.
        metadata = Metadata(
            address=address,
            pages=pages,
            num_results=num_results
        )
        
        # Create a quite event for the task.
        quit_event = threading.Event()
        
        # Add the metadata to the tasks mapping.
        with self._lock:
            self._tasks[metadata.id] = metadata
            
        # Create a future for the for this job and submit it to the thread pool.
        future = self._executer.submit(
            self._execute_scrape_task,
            task_id=metadata.id,
            quit_event=quit_event
        )
        
        # Add the callback function to the future to handle task completion.
        future.add_done_callback(self._get_task_finished_callback())
        
        # Add the future and quit event to the futures mapping.
        with self._lock:
            self._futures[metadata.id] = (future, quit_event)
            
        # Log the creation of the task.
        event_handling_operations_logger.debug(
            f"Task with ID '{metadata.id}' created for address {address} with pages {pages} and num_results {num_results}."
        )
            
        # Return the metadata object for the task.
        return metadata
            
        

    # # This is our worker function...
    # def scrape_address(self, task_id: str, address: tuple, pages: list,
    #                    num_results: int, quit_event: threading.Event = None)  -> Union[list,  None]:
    #     """
    #     Worker function to scrape address from property site. In all cases,
    #     whether the task succeeds or fails, this method will ensure that the
    #     driver is returned to the pool.
    #     """

    #     try:
    #         # Get the id of the thread that is executing this task.
    #         thread_id = threading.get_ident()

    #         # check out a driver from the pool.
    #         with self._lock:
    #             driver = None
    #             while driver is None:
    #                 driver = self._driver_pool.borrow_driver(
    #                 task_id=task_id, thread_id=thread_id)
    #                 time.sleep(10)

    #         # Scrape for the results, hoping there is not error. (TODO: This behavior is inconsistent.)
    #         results = driver.address_search(address, pages, num_results, quit_event)

    #         with self._lock:
    #             self._driver_pool.return_driver(
    #                 task_id=task_id, thread_id=thread_id)

    #         # Return the results.
    #         return results

    #     except Exception as e:
    #         with self._lock:

    #             # Return the driver to the pool if there is an error, if there is a driver that is checked out.
    #             self._driver_pool.return_driver(
    #                 task_id=task_id, thread_id=thread_id, raise_error=False)

    #             # If there is an error, we need to return the driver to the pool.
    #             if task_id in self._tasks:
    #                 self._tasks[task_id].status = Status.FAILED
    #                 self._tasks[task_id].error = e
    #                 if 'results' in locals():
    #                     self.tasks[task_id].result = results
    #                 self._tasks[task_id].finished_at = datetime.now()

    # def post_scrape_task(self,
        #                  address: Tuple[int, str, str],
        #                  pages: List[str],
        #                  num_results: int
        #                  ) -> Metadata:
        # """
        # Create a new scraping task and submit it to the thread pool.
        # This method is needlessly complicated, but it allows to keep
        # track of certain metadata and state changes.
        # Args:
        #     address: Tuple containing number, street, and city.
        #     pages: List of pages to scrape.
        #     num_results: Number of results to return from the scrape (1-10).
        # """
        # try:

        #     # Init new task
        #     metadata = Metadata(
        #         address=address,
        #         pages=pages,
        #         num_results=num_results
        #     )
        #     task_id = metadata.id

        #     # Update tasks and futures
        #     with self._lock:
        #         self._tasks[task_id] = metadata
                
        #     # Create quit event for task
        #     quit_event = threading.Event()
                
        #     # kwargs for the worker function.
        #     kwargs = {
        #         'task_id': task_id,  # Unique task identifier.
        #         # Function to execute in helper worker function/thread.
        #         'func': self.scrape_address,
        #         # Arguments to pass to the worker function.
        #         'args': (task_id, address, pages, num_results, quit_event),
        #     }

        #     # Submit the task to the thread pool.
        #     # The execute task method will handle the execution and status updates and appropriate states changes and error handling.
        #     future = self._executer.submit(self._execute_task, **kwargs)

        #     # Update the futures.
        #     with self._lock:
        #         self._futures[task_id] = (future, quit_event)

        #     # Return the metadata object.
        #     return metadata

        # except Exception as e:

        #     # If a task id is created at this point, get it.
        #     if 'task_id' in locals():
        #         with self._lock:
        #             self._tasks.pop(task_id, None)
        #             self._futures.pop(task_id, None)

        #     # Raise the error to the next scope.
        #     raise RuntimeError(f"Failed to post scrape task: {e}")

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
            task_result = self._tasks.get(task_id, None)
            if not task_result: 
                raise RuntimeError(f"No task was found for task_id: {task_id}")
            if task_result and task_result.status in {Status.COMPLETED, Status.CANCELLED, Status.FAILED}:
                return task_result
        return None
