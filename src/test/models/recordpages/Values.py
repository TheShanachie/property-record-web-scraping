from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ValueItem(BaseModel):
    exempt_land: Optional[str] = Field(..., alias="Exempt Land")
    exempt_building: Optional[str] = Field(..., alias="Exempt Building")
    current_land: Optional[str] = Field(..., alias="Current Land")
    current_building: Optional[str] = Field(..., alias="Current Building")
    current_total: Optional[str] = Field(..., alias="Current Total")
    assessed_land: Optional[str] = Field(..., alias="Assessed Land")
    assessed_building: Optional[str] = Field(..., alias="Assessed Building")
    total_assessed_value: Optional[str] = Field(..., alias="Total Assessed Value")

    @field_validator("*", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    class Config:
        extra = "forbid"
        allow_population_by_field_name = True


class Values(BaseModel):
    values: List[ValueItem] = Field(..., alias="Values")

    class Config:
        extra = "forbid"
        allow_population_by_field_name = True
