from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional, List, Tuple
from uuid import uuid4
from enum import Enum
from datetime import datetime
from models import Record

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
    
    # Timestamp Data
    created_at: str = Field(default_factory=lambda: datetime.now(), description="Creation timestamp")
    finished_at: Optional[str] = Field(None, description="Completion timestamp")
    
    # Status Data
    status: Status = Field(Status.CREATED, description="Current status of the task (e.g., 'pending', 'running', 'completed', 'failed', 'cancelled')")
    status_code: int = Field(200, description='HTTP status code representing the task status')
    
    # Input Data
    address: Tuple[int, str, str] = Field(..., description="Tuple containing number, street, and city")
    pages: List[str] = Field(..., description="List of pages to scrape")
    num_results: int = Field(..., description="Number of results to return from the scrape", ge=1, le=10)
    
    # Result
    result: Record = Field(None, "The result data from a webscraping job.")
    
    # Error Data
    error_message: Optional[str] = Field(None, description="Error message if the task failed")
    error_code: Optional[int] = Field(None, description="Error code if the task failed")
    
    
    
    