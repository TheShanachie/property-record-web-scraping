from .models import ActionInput, ActionOutput
from .task_manager import TaskManager
from pydantic import validate_call

class EventsHandler():
    def __init__(self, max_drivers: int = 5, max_workers: int = 5, cleanup_interval: int = 3600):
        # Initialize any necessary resources or configurations here
        self._task_manager = TaskManager(max_drivers=max_drivers, 
                                         max_workers=max_workers, 
                                         cleanup_interval=cleanup_interval)
        
    def shutdown(self):
        """
            This function is called when the application is shutting down. It cleans up any resources
            that were initialized in the constructor.
        """
        self._task_manager.shutdown()

    @validate_call
    def health(self) -> ActionOutput.Health:
        """
            This function checks the health of the server and returns a status message.
            
            # TODO: There are so many things we can do here to improve visibility.
        """
        return ActionOutput.Health(status="healthy", error=None, status_code=200)

    @validate_call
    def tasks(self) -> ActionOutput.Tasks:
        """
            This function retrieves all tasks from the TaskManager and returns them in a structured format.
            
            # TODO: Implementation of task category filtering is quite easy.
        """
        tasks = self._task_manager.get_all_tasks()
        return ActionOutput.Tasks(tasks=tasks, error=None, status_code=200)
    
    @validate_call
    def scrape(self, arguments: ActionInput.Scrape) -> ActionOutput.Scrape:
        """ 
            Function to add a scrape task to the TaskManaget thread pool. 
        """
        
        try: 
            # Extract the arguments from the input model
            address = arguments['address']
            pages = arguments['pages']
            num_results = arguments['num_results']
            
            # Post the scrape task to the TaskManager
            metadata = self._task_manager.post_scrape_task(
                address=address,
                pages=pages,
                num_results=num_results
            )
            return ActionOutput.Scrape(metadata=metadata)
        
        except Exception as e:
            
            # Get the error message and status code
            error_message = str(e)
            status_code = 500  # Default to internal server error
            
            if 'metadata' in locals():
                # If metadata was created before the exception, return it and error data.
                return ActionOutput.Scrape(metadata=metadata, 
                                           error=error_message, 
                                           status_code=status_code)
            else: 
                # If metadata was not created, return only error data.
                return ActionOutput.Scrape(error=error_message, 
                                           status_code=status_code)
    
    @validate_call
    def cancel(self, arguments: ActionInput.Cancel) -> ActionOutput.Cancel:
        """ 
            This function is currently not implemented. It is a placeholder for future functionality.
            
            # TODO: Implement cancel functionality
        """
        
        return ActionOutput.Cancel(
            metadata=None,
            error="Cancel functionality is not implemented yet.",
            status_code=501  # Not Implemented
        )
    
    @validate_call
    def status(self, arguments: ActionInput.Status) -> ActionOutput.Status:
        """
            Function to get the status/metadata of a specific task. This is a generic method
            that simply returns the most recently available metadata for the task at the time
            of the request. This may or may not be the final metadata for the task.
        """
        task_id = arguments['task_id']
        metadata = self._task_manager.get_task_status(task_id=task_id)
        return ActionOutput.Status(metadata=metadata, 
                                   error=None, 
                                   status_code=200)
    
    @validate_call
    def result(self, arguments: ActionInput.Result) -> ActionOutput.Result:
        """
            Function to get the result of a specific task. This method returns the 
            final metadata for the task, iff the task has been completed. Otherwise,
            the method will return nothing in terms of the task metadata object.
        """
        task_id = arguments['task_id']
        metadata = self._task_manager.get_task_result(task_id=task_id)
        return ActionOutput.Result(metadata=metadata,
                                   error=None, 
                                   status_code=200)
    
    @validate_call
    def wait(self, arguments: ActionInput.Wait) -> ActionOutput.Wait:
        """
            Function to wait for a specific task to complete. This method will block until the task
            has been completed, and then return the final metadata for the task. This task does not
            acknowledge the timeout for the moment, but it can be implemented in the future. At the
            moment, the timeout is set to 60 seconds, which is the default for the TaskManager.
            
            # TODO: Implement timeout functionality for waiting on tasks. Implement response codes
            and error messages for the timeout case.
        """
        task_id = arguments['task_id']
        metadata = self._task_manager.wait_for_task(task_id=task_id, timeout=60)
        return ActionOutput.Wait(metadata=metadata,
                                 error=None, 
                                 status_code=200)