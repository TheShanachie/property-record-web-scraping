from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Tuple
from uuid import uuid4
from enum import Enum

class ActionType(str, Enum):
    """Enumeration for possible actions."""
    SCRAPE = "scrape"
    CANCEL = "cancel"
    STATUS = "status"
    RESULT = "result"
    WAIT = "wait"
    TASKS = "tasks"
    HEALTH = "health"
 
class ScrapeInput(BaseModel):
    """Model for scrape input data."""
    address: Tuple[int, str, str] = Field(..., description="Tuple containing number, street, and city")
    pages: List[str] = Field(..., description="List of pages to scrape")
    num_results: int = Field(..., description="Number of results to return from the scrape", ge=1, le=10)
    
    @field_validator('pages', mode='after')
    @classmethod
    def validate_pages(cls, v):
        possible_pages = ["Parcel", "Owner", "Multi-Owner", "Residential", "Land", "Values", "Homestead", "Sales"] # The currently supported pages.
        if set(v).issubset(set(possible_pages)):
            raise ValueError(f"Invalid page in 'pages' list. Must be any of {possible_pages}")
        return v
    
class TaskInput(BaseModel):
    """
    Model for simple task data input.
    Used fot the action 'cancel', 'status', 'result', and 'wait'.
    """
    task_id: str = Field(..., description="ID of the task to cancel")

    
class TasksOutput(BaseModel):
    """Model for tasks response."""
    tasks: Dict[str, dict] = Field(..., description="Dictionary of task IDs and their statuses")
    count: int = Field(..., description="Total number of tasks")


class HealthOutput(BaseModel):
    """Health check response model."""
    health: str = Field(..., description="Health status of the service")
    
    @field_validator('health', mode='after')
    @classmethod
    def health_match(cls, v):
        if not v in ["healthy", "unhealthy"]:
            raise ValueError("Health status must be 'healthy' or 'unhealthy'")
        return v
    
class TaskOutput(BaseModel):
    pass



    
