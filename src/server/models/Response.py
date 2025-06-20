from Metadata import Metadata
from Action import Action
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class Response(BaseModel):
    """Response model for the web scraping service."""
    
    # Metadata about the response
    metadata: Metadata = Field(..., description="Metadata about the task, including status and timestamps")
    
    # Action performed
    action: Action = Field(..., description="Action that was performed (e.g., scrape, cancel, status)")