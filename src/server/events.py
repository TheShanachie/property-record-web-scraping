from typing_extensions import TypedDict, Unpack
from driver_pool import DriverPool
from thread_pool import WebScrapingThreadPool 
from models import ActionInput, ActionOutput
from models.Metadata import Metadata, TaskType, Status
from pydantic import validate_call
from task_manager import TaskManager

class EventsHandler():
    def __init__(self):
        # Initialize any necessary resources or configurations here
        self._task_manager = TaskManager(max_drivers=5, 
                                         max_workers=5, 
                                         cleanup_interval=3600)

    @validate_call
    def health(self) -> ActionOutput.Health:
        """
        This function checks the health of the server and returns a status message.
        """
        # TODO: There are so many things we can do here to improve visibility.
        return ActionOutput.Health(status="healthy")
        

    @validate_call
    def tasks(self) -> ActionOutput.Tasks:
        """
        This function retrieves all tasks from the TaskManager and returns them in a structured format.
        """
        # TODO: Implementation of task category filtering is quite easy.
        return ActionOutput.Tasks(tasks=self._task_manager.get_all_tasks())
    
    @validate_call
    def scrape(self, arguments: ActionInput.Scrape) -> ActionOutput.Scrape:
        """ Function to add a scrape task to the TaskManaget thread pool. """
        
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
    
    @validate_call
    def cancel(self, arguments: ActionInput.Cancel) -> ActionOutput.Cancel:
        """ This function is currently not implemented. It is a placeholder for future functionality. """
        pass
    
    @validate_call
    def status(self, arguments: ActionInput.Status) -> ActionOutput.Status:
        """"""
        task_id = arguments['task_id']
        metadata = self._task_manager.get_task_status(task_id=task_id)
        return ActionOutput.Status(metadata=metadata)
    
    @validate_call
    def result(self, arguments: ActionInput.Result) -> ActionOutput.Result:
        """"""
        task_id = arguments['task_id']
        metadata = self._task_manager.get_task_result(task_id=task_id)
        return ActionOutput.Result(metadata=metadata)
    
    @validate_call
    def wait(self, arguments: ActionInput.Wait) -> ActionOutput.Wait:
        """"""
        task_id = arguments['task_id']
        metadata = self._task_manager.wait_for_task(task_id=task_id)
        return ActionOutput.Wait(metadata=metadata)