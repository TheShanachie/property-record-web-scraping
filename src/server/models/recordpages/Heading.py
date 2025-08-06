from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Heading(BaseModel):
    """Property heading information with owner and address details."""
    
    parid: Optional[str] = Field(alias="PARID")
    owner: Optional[str] = Field(alias="OWNER")
    address: Optional[str] = Field(alias="ADDRESS")

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert strings containing only whitespace to None."""
        if isinstance(v, str) and not v.strip():
            return None
        return v

    class Config:
        populate_by_name = True
        extra = "forbid"