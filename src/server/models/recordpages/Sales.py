from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SalesItem(BaseModel):
    date_recorded: Optional[str] = Field(..., alias="Date Recorded")
    new_owner: Optional[str] = Field(..., alias="New Owner")
    sale_price: Optional[str] = Field(..., alias="Sale Price")
    old_owner: Optional[str] = Field(..., alias="Old Owner")

    @field_validator("*", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    class Config:
        extra = "forbid"
        validate_by_name = True


class SalesDetailItem(BaseModel):
    sale_date: Optional[str] = Field(..., alias="Sale Date")
    sale_price: Optional[str] = Field(..., alias="Sale Price")
    new_owner: Optional[str] = Field(..., alias="New Owner")
    previous_owner: Optional[str] = Field(..., alias="Previous Owner")
    recorded_date: Optional[str] = Field(..., alias="Recorded Date")
    deed_book: Optional[str] = Field(..., alias="Deed Book")
    deed_page: Optional[str] = Field(..., alias="Deed Page")

    @field_validator("*", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    class Config:
        extra = "forbid"
        validate_by_name = True


class Sales(BaseModel):
    sales: List[SalesItem] = Field(..., alias="Sales\n  ")
    sales_detail: List[SalesDetailItem] = Field(..., alias="Sales Detail\n  ")

    class Config:
        extra = "forbid"
        validate_by_name = True
