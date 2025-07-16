from .Metadata import Metadata
from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import uuid4
from enum import Enum

class InputModel(BaseModel):
    """
    Base model for input data.
    This class is used to define the common fields and validation logic for all input models.
    """
    model_config = ConfigDict(
        extra='forbid',  # Forbid extra fields not defined in the model
        validate_assignment=True,  # Validate assignments to fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )
    
class Scrape(InputModel):
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


class Cancel(InputModel):
    """
    Model for simple task data input.
    Used fot the action 'cancel', 'status', 'result', and 'wait'.
    """
    task_id: str = Field(..., description="ID of the task to cancel")


class Status(InputModel):
    """
    Model for simple task data input.
    Used fot the action 'cancel', 'status', 'result', and 'wait'.
    """
    task_id: str = Field(..., description="ID of the task to cancel")


class Result(InputModel):
    """
    Model for simple task data input.
    Used fot the action 'cancel', 'status', 'result', and 'wait'.
    """
    task_id: str = Field(..., description="ID of the task to cancel")


class Wait(InputModel):
    """
    Model for simple task data input.
    Used fot the action 'cancel', 'status', 'result', and 'wait'.
    """
    task_id: str = Field(..., description="ID of the task to cancel")


class Tasks(InputModel):
    """Model for tasks input data. There is no input data for this action."""
    pass


class Health(InputModel):
    """Model for health input data. There is no input data for this action."""
    pass