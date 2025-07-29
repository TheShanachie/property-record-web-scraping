from .Metadata import Metadata
from .SafeErrorMixin import SafeErrorMixin
from .Record import Record
from typing import Optional, List, Dict, Tuple, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator, field_serializer
from uuid import uuid4
from enum import Enum

    
class OutputModel(SafeErrorMixin, BaseModel):
    """
    Base model for output data.
    This class is used to define the common fields and validation logic for all output models.
    """
    
    # Model Config
    model_config = ConfigDict(
        # extra='forbid',  # Forbid extra fields not defined in the model
        validate_assignment=True,  # Validate assignments to fields
        arbitrary_types_allowed=True,  # Allow arbitrary types
    )
    
    # Error Data
    error_message: Optional[str] = Field(None, description="Error message if any error occurred during processing of the request")
    status_code: Optional[int] = Field(None, description="HTTP status code for the response, e.g., 200 for success, 400 for bad request, etc.")
    
    # Extra
    extra: Optional[Dict[str, Any]] = Field(None, description="Any extra data that might be needed for the response")
    
    # to json flask response
    def json_dump(self) -> Dict[str, Any]:
        """
        Convert the model to a JSON-compatible dictionary.
        """
        return self.model_dump(mode='json', exclude_none=False), self.status_code if self.status_code else 200
    
class Scrape(OutputModel):
    """Model for scrape input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(None, description="Metadata about the task, including status and timestamps")
    

class Cancel(OutputModel):
    """Model for cancel input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(None, description="Metadata about the task, including status and timestamps")


class Status(OutputModel):
    """Model for status input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(None, description="Metadata about the task, including status and timestamps")


class Result(OutputModel):
    """Model for result input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(None, description="Metadata about the task, including status and timestamps")


class Wait(OutputModel):
    """Model for wait input data."""
    
    # Metadata about the response
    metadata: Metadata = Field(None, description="Metadata about the task, including status and timestamps")


class Tasks(OutputModel):
    """Model for tasks input data."""

    # Actual Data -> List of metadata objects for the current tasks.
    tasks: List[Metadata] = Field(None, description="List of metadata objects for the current tasks")


class Health(OutputModel):
    """Model for health input data."""
    
    # Actual Data
    health: str = Field(None, description="Health status of the service")
    
    # Driver pool info
    driver_pool: Optional[Dict[Any, Any]] = Field(None, description="Information about the driver pool, including available and active drivers")
    
    @field_validator('health', mode='after')
    @classmethod
    def health_match(cls, v):
        if not v in ["healthy", "unhealthy"]:
            raise ValueError("Health status must be 'healthy' or 'unhealthy'")
        return v