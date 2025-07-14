from Metadata import Metadata
from Record import Record
from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import uuid4
from enum import Enum

    
class OutputModel(BaseModel):
    """
    Base model for output data.
    This class is used to define the common fields and validation logic for all output models.
    """
    model_config = ConfigDict(
        extra='forbid',  # Forbid extra fields not defined in the model
        validate_assignment=True,  # Validate assignments to fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )

class Scrape(OutputModel):
    """Model for scrape input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(..., description="Metadata about the task, including status and timestamps")
    

class Cancel(OutputModel):
    """Model for cancel input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(..., description="Metadata about the task, including status and timestamps")


class Status(OutputModel):
    """Model for status input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(..., description="Metadata about the task, including status and timestamps")


class Result(OutputModel):
    """Model for result input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(..., description="Metadata about the task, including status and timestamps")


class Wait(OutputModel):
    """Model for wait input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(..., description="Metadata about the task, including status and timestamps")


class Tasks(OutputModel):
    """Model for tasks input data."""

    # Actual Data -> List of metadata objects for the current tasks.
    tasks: List[Metadata] = Field(..., description="List of metadata objects for the current tasks")

class Health(OutputModel):
    """Model for health input data."""
    
    # Actual Data
    health: str = Field(..., description="Health status of the service")
    
    @field_validator('health', mode='after')
    @classmethod
    def health_match(cls, v):
        if not v in ["healthy", "unhealthy"]:
            raise ValueError("Health status must be 'healthy' or 'unhealthy'")
        return v