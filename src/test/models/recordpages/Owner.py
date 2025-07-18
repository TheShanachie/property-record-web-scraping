from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class CurrentOwnerDetailRecord(BaseModel):
    """Individual current owner detail record with owner information."""
    
    names: Optional[str] = Field(alias="Name(s)")
    in_care_of: Optional[str] = Field(alias="In Care of")
    mailing_address: Optional[str] = Field(alias="Mailing Address")
    city_state_zip_code: Optional[str] = Field(alias="City, State, Zip Code")
    book: Optional[str] = Field(alias="Book")
    page: Optional[str] = Field(alias="Page")

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


class OwnerHistoryRecord(BaseModel):
    """Individual owner history record with sale information."""
    
    current_owner: Optional[str] = Field(alias="Current Owner")
    previous_owner: Optional[str] = Field(alias="Previous Owner")
    sale_date: Optional[str] = Field(alias="Sale Date")
    price: Optional[str] = Field(alias="Price")
    book: Optional[str] = Field(alias="Book")
    page: Optional[str] = Field(alias="Page")

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


class Owner(BaseModel):
    """Root model containing current owner details and owner history records."""
    
    current_owner_details: List[CurrentOwnerDetailRecord] = Field(alias="Current Owner Details")
    owner_history: List[OwnerHistoryRecord] = Field(alias="Owner History\n  ")

    class Config:
        populate_by_name = True
        extra = "forbid"