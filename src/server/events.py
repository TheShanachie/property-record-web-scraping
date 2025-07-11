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
        pass

    @validate_call
    def tasks(self) -> ActionOutput.Tasks:
        pass
    
    @validate_call
    def scrape(self, **kwargs: Unpack[ActionInput.Scrape]) -> ActionOutput.Scrape:
        """ Function to add a scrape task to the TaskManaget thread pool.
        
        Args:
            ...
            
        Return: 
            ...
        """
        
        pass
    
    @validate_call
    def cancel(self, **kwargs: Unpack[ActionInput.Cancel]) -> ActionOutput.Cancel:
        pass
    
    @validate_call
    def status(self, **kwargs: Unpack[ActionInput.Status]) -> ActionOutput.Status:
        pass
    
    @validate_call
    def result(self, **kwargs: Unpack[ActionInput.Result]) -> ActionOutput.Result:
        pass
    
    @validate_call
    def wait(self, **kwargs: Unpack[ActionInput.Wait]) -> ActionOutput.Wait:
        pass