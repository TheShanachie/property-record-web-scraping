from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class MultiOwnerDetailRecord(BaseModel):
    """Individual multi-owner detail record with owner information."""
    
    name: Optional[str] = Field(alias="Name")
    in_care_of: Optional[str] = Field(alias="In Care of")
    mailing_address: Optional[str] = Field(alias="Mailing Address")
    book: Optional[str] = Field(alias="Book")
    page: Optional[str] = Field(alias="Page")
    deed_2: Optional[str] = Field(alias="Deed 2")
    deed_3: Optional[str] = Field(alias="Deed 3")
    deed_4: Optional[str] = Field(alias="Deed 4")
    deed_5: Optional[str] = Field(alias="Deed 5")

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


class MultiOwner(BaseModel):
    """Root model containing multi-owner details and owner history records."""
    
    multi_owner_details: List[MultiOwnerDetailRecord] = Field(alias="Multi-Owner Details")
    owner_history: List[OwnerHistoryRecord] = Field(alias="Owner History\n  ")

    class Config:
        populate_by_name = True
        extra = "forbid"