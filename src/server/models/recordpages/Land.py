from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from ..SanitizeMixin import SanitizedBaseModel

class LandRecord(SanitizedBaseModel):
    """Individual land record with basic land information."""
    
    line_number: Optional[str] = Field(alias="Line #")
    type: Optional[str] = Field(alias="Type")
    code: Optional[str] = Field(alias="Code")
    acres: Optional[str] = Field(alias="Acres")

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


class LandDetailRecord(SanitizedBaseModel):
    """Individual land detail record with detailed land information."""
    
    line_number: Optional[str] = Field(alias="Line Number")
    land_type: Optional[str] = Field(alias="Land Type")
    land_code: Optional[str] = Field(alias="Land Code")
    frontage: Optional[str] = Field(alias="Frontage")
    depth: Optional[str] = Field(alias="Depth")
    units: Optional[str] = Field(alias="Units")
    cama_square_feet: Optional[str] = Field(alias="CAMA Square Feet")
    cama_acres: Optional[str] = Field(alias="CAMA Acres")

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


class Land(SanitizedBaseModel):
    """Root model containing land records and land detail records."""
    
    land: List[LandRecord] = Field(alias="Land")
    land_details: List[LandDetailRecord] = Field(alias="Land Details")

    class Config:
        populate_by_name = True
        extra = "forbid"