import threading
import uuid
import json
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Tuple, Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import time

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class TaskData:
    task_id: str
    status: TaskStatus
    args: tuple
    kwargs: dict
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskData to dictionary for JSON serialization"""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'args': self.args,
            'kwargs': self.kwargs,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }   
        

class WebScrapingThreadPool:
    """
    Thread pool manager for web scraping operations.
    Provides async task submission and status tracking.
    """
    
    def __init__(self, max_workers: int = 5, cleanup_interval: int = 3600):
        """
        Initialize the thread pool manager.
        
        Args:
            max_workers: Maximum number of concurrent threads
            cleanup_interval: Interval in seconds to cleanup completed tasks (default: 1 hour)
        """
        self.max_workers = max_workers
        self.cleanup_interval = cleanup_interval
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, TaskData] = {}
        self.futures: Dict[str, Future] = {}
        self._lock = threading.Lock()
        
        # Start cleanup thread
        self._shutdown = False
        self._cleanup_thread = threading.Thread(target=self._cleanup_completed_tasks, daemon=True)
        self._cleanup_thread.start()
        
    
    def submit_task(self, func: Callable, args: Tuple = (), kwargs: Dict = None) -> TaskData:
        """
        Submit a task to the thread pool.
        
        Args:
            func: Function to execute
            args: Additional positional arguments for the function
            kwargs: Additional keyword arguments for the function
            
        Returns:
            TaskData: TaskData Object w/ unique ids.
        """
        if kwargs is None:
            kwargs = {}
            
        task_id = str(uuid.uuid4())
        
        # Create task result tracker
        task_result = TaskData(task_id=task_id, status=TaskStatus.PENDING, args=args, kwargs=kwargs)
        
        with self._lock:
            self.tasks[task_id] = task_result
        
        # Submit to thread pool - pass task_data as first argument
        future = self.executor.submit(self._execute_task, task_id, func, args, kwargs)
        
        with self._lock:
            self.futures[task_id] = future
            
        return task_result
    
    def _execute_task(self, task_id: str, func: Callable, args: Tuple, kwargs: Dict):
        """Internal method to execute task and update status"""
        try:
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.RUNNING
                    self.tasks[task_id].started_at = datetime.now()
            
            # Execute the function with argument
            result = func(*args, **kwargs)
            
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.COMPLETED
                    self.tasks[task_id].result = result
                    self.tasks[task_id].completed_at = datetime.now()
                    
        except Exception as e:
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.ERROR
                    self.tasks[task_id].error = str(e)
                    self.tasks[task_id].completed_at = datetime.now()
    
    def get_task_status(self, task_id: str) -> TaskData:
        """
        Get the current status of a task.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            TaskData object with relevant details.
        """
        with self._lock:
            task_result = self.tasks.get(task_id)
            if task_result:
                return task_result
        return None
    
    def get_task_result(self, task_id: str) -> TaskData:
        """
        Get the result of a completed task.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            TaskData object with relevant details.
        """
        with self._lock:
            task_result = self.tasks.get(task_id)
            if task_result and task_result.status == TaskStatus.COMPLETED:
                return task_result
        return None
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> TaskData:
        """
        Wait for a task to complete and return its status.
        
        Args:
            task_id: Unique task identifier
            timeout: Maximum time to wait in seconds
            
        Returns:
            TaskData with final task status or None if timeout/not found
        """
        future = self.futures.get(task_id)
        if not future:
            return None
            
        try:
            future.result(timeout=timeout)
        except Exception:
            pass  # Exception already handled in _execute_task
            
        return self.get_task_status(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Attempt to cancel a pending task.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            bool: True if successfully cancelled, False otherwise
        """
        future = self.futures.get(task_id)
        if future and future.cancel():
            with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.ERROR
                    self.tasks[task_id].error = "Task cancelled"
                    self.tasks[task_id].completed_at = datetime.now()
            return True
        return False
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks"""
        with self._lock:
            return {task_id: task.to_dict() for task_id, task in self.tasks.items()}
    
    def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active (pending/running) tasks"""
        with self._lock:
            active_statuses = {TaskStatus.PENDING, TaskStatus.RUNNING}
            return {
                task_id: task
                for task_id, task in self.tasks.items() 
                if task.status in active_statuses
            }
    
    def _cleanup_completed_tasks(self):
        """Background thread to cleanup old completed tasks"""
        while not self._shutdown:
            try:
                time.sleep(self.cleanup_interval)
                current_time = datetime.now()
                
                with self._lock:
                    completed_statuses = {TaskStatus.COMPLETED, TaskStatus.ERROR}
                    tasks_to_remove = []
                    
                    for task_id, task in self.tasks.items():
                        if (task.status in completed_statuses and 
                            task.completed_at and 
                            (current_time - task.completed_at).seconds > self.cleanup_interval):
                            tasks_to_remove.append(task_id)
                    
                    for task_id in tasks_to_remove:
                        self.tasks.pop(task_id, None)
                        self.futures.pop(task_id, None)
                        
            except Exception as e:
                print(f"Cleanup thread error: {e}")
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the thread pool.
        
        Args:
            wait: Whether to wait for pending tasks to complete
        """
        self._shutdown = True
        self.executor.shutdown(wait=wait)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()