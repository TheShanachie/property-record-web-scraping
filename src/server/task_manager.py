from models.Metadata import Metadata, TaskType, Status
from models.ActionInput import InputModel
from models.ActionOutput import OutputModel
from typing import List, Tuple, Union

class TaskManager:
    """
    TaskManager is responsible for managing tasks in the application.
    It provides methods to handle task-related operations such as health checks,
    task management, scraping, cancellation, status checking, result retrieval, and waiting.
    """

    def __init__(self, thread_pool, driver_pool):
        self._thread_pool = thread_pool
        self._driver_pool = driver_pool
        
        # List to store tasks as simple in memory tuples. - Can be improved.
        self._living_tasks = List[Tuple[TaskType, Metadata, Union[InputModel, None]]]
        self._dead_tasks = List[Tuple[TaskType, Union[OutputModel, None]]]
        
        
    def create_task(self, task_type: TaskType) -> Tuple:
        """
        Create a new task with initial metadata.
        """
        task_metadata = Metadata(
            task_type=task_type,
            status=Status.CREATED,
        )
        
        return (task_type, task_metadata, None, None)