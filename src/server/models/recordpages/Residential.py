from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from ..SanitizeMixin import SanitizedBaseModel

class ResidentialItem(SanitizedBaseModel):
    card: Optional[str] = Field(..., alias="Card")
    year_built: Optional[str] = Field(..., alias="Year Built")
    remodeled_year: Optional[str] = Field(..., alias="Remodeled Year")
    land_use_code: Optional[str] = Field(..., alias="Land Use Code")
    total_square_feet_living_area: Optional[str] = Field(..., alias="Total Square Feet Living Area")
    number_of_stories: Optional[str] = Field(..., alias="Number of Stories")
    grade: Optional[str] = Field(..., alias="Grade")
    cdu: Optional[str] = Field(..., alias="CDU")
    building_style: Optional[str] = Field(..., alias="Building Style")
    total_rooms: Optional[str] = Field(..., alias="Total Rooms")
    bedrooms: Optional[str] = Field(..., alias="Bedrooms")
    full_baths: Optional[str] = Field(..., alias="Full Baths")
    half_baths: Optional[str] = Field(..., alias="Half Baths")
    additional_fixtures: Optional[str] = Field(..., alias="Additional Fixtures")
    total_fixtures: Optional[str] = Field(..., alias="Total Fixtures")
    heat_air_cond: Optional[str] = Field(..., alias="Heat/Air Cond")
    heating_fuel_type: Optional[str] = Field(..., alias="Heating Fuel Type")
    heating_system_type: Optional[str] = Field(..., alias="Heating System Type")
    attic_code: Optional[str] = Field(..., alias="Attic Code")
    unfinished_area: Optional[str] = Field(..., alias="Unfinished Area")
    rec_room_area: Optional[str] = Field(..., alias="Rec Room Area")
    finished_basement_area: Optional[str] = Field(..., alias="Finished Basement Area")
    fireplace_openings: Optional[str] = Field(..., alias="Fireplace Openings")
    fireplace_stacks: Optional[str] = Field(..., alias="Fireplace Stacks")
    prefab_fireplaces: Optional[str] = Field(..., alias="Prefab Fireplaces")
    basement_garage_number_of_cars: Optional[str] = Field(..., alias="Basement Garage (Number of Cars)")
    condo_level: Optional[str] = Field(..., alias="Condo Level")
    condo_townhouse_type: Optional[str] = Field(..., alias="Condo/Townhouse Type")
    basement: Optional[str] = Field(..., alias="Basement")
    exterior_wall_material: Optional[str] = Field(..., alias="Exterior Wall Material")
    physical_condition: Optional[str] = Field(..., alias="Physical Condition")
    # period: Optional[str] = Field(..., alias=".")

    @field_validator("*", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    class Config:
        extra = "forbid"
        validate_by_name = True

class Residential(SanitizedBaseModel):
    residential: List[ResidentialItem] = Field(..., alias="Residential")

    class Config:
        extra = "forbid"
        validate_by_name = True
