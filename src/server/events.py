from typing_extensions import TypedDict, Unpack
from driver_pool import DriverPool
from thread_pool import WebScrapingThreadPool 
from models import ActionInput, ActionOutput
from pydantic import validate_call

class EventsHandler():
    def __init__(self, driver_pool: DriverPool, thread_pool: WebScrapingThreadPool):
        # Initialize any necessary resources or configurations here
        self._driver_pool = driver_pool
        self._thread_pool = thread_pool

    @validate_call
    def health(self) -> ActionOutput.Health:
        pass

    @validate_call
    def tasks(self) -> ActionOutput.Tasks:
        pass
    
    @validate_call
    def scrape(self, **kwargs: Unpack[ActionInput.Scrape]) -> ActionOutput.Scrape:
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