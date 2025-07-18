from pydantic import BaseModel, Field, ConfigDict, computed_field, field_serializer, field_validator
from typing import Optional, List, Tuple, Union
from uuid import uuid4
from enum import Enum
from datetime import datetime
from .Record import Record
from .SafeErrorMixin import SafeErrorMixin

class Status(str, Enum):
    """Enumeration for task status"""
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPING = "stopping"
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


class Metadata(SafeErrorMixin, BaseModel):
    """Metadata for a task, including status and timestamps."""
    
    # Config
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # General Information
    id: str = Field(default_factory=lambda: uuid4().hex, alias="task_id", description="Unique identifier for the task")
    
    # Timestamp Data
    created_at: Union[str, datetime] = Field(default_factory=lambda: datetime.now(), description="Creation timestamp")
    started_at: Optional[Union[str, datetime]] = Field(None,description="Time that service started execution")
    finished_at: Optional[Union[str, datetime]] = Field(None, description="Completion timestamp")
    
    # Status Data
    status: Status = Field(Status.CREATED, description="Current status of the task (e.g., 'pending', 'running', 'completed', 'failed', 'cancelled')")
    status_code: int = Field(200, description='HTTP status code representing the task status')
    
    # Input Data
    address: Tuple[int, str, str] = Field(..., description="Tuple containing number, street, and city")
    pages: List[str] = Field(..., description="List of pages to scrape")
    num_results: int = Field(..., description="Number of results to return from the scrape", ge=1, le=10)
    
    # Result
    result: Record = Field(None, description="The result data from a webscraping job.")
    
    # Error Data
    error_code: Optional[int] = Field(None, description="Error code if the task failed")
    error_message: Optional[str] = Field(None, description="Error message if appropriate")

    
    
    
    