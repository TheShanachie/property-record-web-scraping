from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, List
from uuid import uuid4
from enum import Enum
from datetime import datetime

class Status(str, Enum):
    """Enumeration for task status"""
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
class TaskType(str, Enum):
    """Enumeration for task type"""
    SCRAPE = "scrape"
    CANCEL = "cancel"
    STATUS = "status"
    RESULT = "result"
    WAIT = "wait"
    TASKS = "tasks"
    HEALTH = "health"

class Metadata(BaseModel):
    """Metadata for a task, including status and timestamps."""
    
    # General Information
    id: str = Field(default_factory=lambda: uuid4().hex)
    
    # Task Type
    task_type: TaskType = Field(..., description="Type of the task (e.g., 'scrape', 'cancel', 'status', 'result', 'wait', 'tasks', 'health')")
    
    # Timestamp Data
    created_at: str = Field(default_factory=lambda: datetime.now(), description="Creation timestamp")
    finished_at: Optional[str] = Field(None, description="Completion timestamp")
    
    # Status Data
    status: Status = Field(..., description="Current status of the task (e.g., 'pending', 'running', 'completed', 'failed', 'cancelled')")
    status_code: int = Field(200, description='HTTP status code representing the task status')
    
    # Input Data
    input_data: Optional[dict] = Field(None, description="Input data for a task.")
    
    # Error Data
    error_message: Optional[str] = Field(None, description="Error message if the task failed")
    error_code: Optional[int] = Field(None, description="Error code if the task failed")
    
    # Custom setter for status to ensure valid transitions
    def set_status(self, new_status: Status):
        """Set the status of the task with validation."""
        if new_status not in Status:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        if new_status == Status.COMPLETED:
            self.finished_at = datetime.now()
        elif new_status in [Status.FAILED, Status.CANCELLED]:
            self.finished_at = datetime.now()
            self.error_message = f"Task ended with status: {new_status}"
            self.error_code = 500
        else:
            self.finished_at = None
    
    
    
    