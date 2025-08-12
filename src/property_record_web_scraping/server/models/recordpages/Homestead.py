from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from ..SanitizeMixin import SanitizedBaseModel


class HomesteadRecord(SanitizedBaseModel):
    """Individual homestead record with property details."""
    
    homestead_denied: Optional[str] = Field(alias="Homestead Denied")
    homestead_farmstead: Optional[str] = Field(alias="Homestead/Farmstead")
    approved: Optional[str] = Field(alias="Approved")
    date_rec_d: Optional[str] = Field(alias="Date Rec'd")
    homestead_effective_year: Optional[str] = Field(alias="Homestead Effective Year")
    farmstead_effective_year: Optional[str] = Field(alias="Farmstead Effective Year")

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


class Homestead(SanitizedBaseModel):
    """Root model containing a list of homestead records."""
    
    homestead: List[HomesteadRecord] = Field(alias="Homestead")

    class Config:
        populate_by_name = True
        extra = "forbid"