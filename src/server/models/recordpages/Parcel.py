from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from ..SanitizeMixin import SanitizedBaseModel

class ParcelRecord(SanitizedBaseModel):
    """Individual parcel record with property details."""
    
    property_location: Optional[str] = Field(alias="Property Location")
    unit_desc: Optional[str] = Field(alias="Unit Desc")
    unit_number: Optional[str] = Field(alias="Unit #")
    city: Optional[str] = Field(alias="City")
    state: Optional[str] = Field(alias="State")
    zip_code: Optional[str] = Field(alias="Zip Code")
    neighborhood_valuation_code: Optional[str] = Field(alias="Neighborhood Valuation Code")
    trailer_description: Optional[str] = Field(alias="Trailer Description")
    municipality: Optional[str] = Field(alias="Municipality")
    classification: Optional[str] = Field(alias="Classification")
    land_use_code: Optional[str] = Field(alias="Land Use Code")
    school_district: Optional[str] = Field(alias="School District")
    topography: Optional[str] = Field(alias="Topography")
    utilities: Optional[str] = Field(alias="Utilities")
    street_road: Optional[str] = Field(alias="Street/Road")
    total_cards: Optional[str] = Field(alias="Total Cards")
    living_units: Optional[str] = Field(alias="Living Units")
    cama_acres: Optional[str] = Field(alias="CAMA Acres")
    homestead_farmstead: Optional[str] = Field(alias="Homestead /Farmstead")
    approved: Optional[str] = Field(alias="Approved?")

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


class ParcelMailingAddressRecord(SanitizedBaseModel):
    """Individual parcel mailing address record."""
    
    in_care_of: Optional[str] = Field(alias="In Care of")
    name_s: Optional[str] = Field(alias="Name(s)")
    mailing_address: Optional[str] = Field(alias="Mailing Address")
    city_state_zip_code: Optional[str] = Field(alias="City, State, Zip Code")

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


class AlternateAddressRecord(SanitizedBaseModel):
    """Individual alternate address record."""
    
    alternate_address: Optional[str] = Field(alias="Alternate Address")
    city: Optional[str] = Field(alias="City")
    state: Optional[str] = Field(alias="State")
    zip: Optional[str] = Field(alias="Zip")

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


class ActFlagsRecord(SanitizedBaseModel):
    """Individual ACT flags record with various act and exemption information."""
    
    act_319_515: Optional[str] = Field(alias="Act 319/515")
    lerta: Optional[str] = Field(alias="LERTA")
    act_43: Optional[str] = Field(alias="Act 43")
    act_66: Optional[str] = Field(alias="Act 66")
    act_4_149: Optional[str] = Field(alias="Act 4/149")
    koz: Optional[str] = Field(alias="KOZ")
    tif_expiration_date: Optional[str] = Field(alias="TIF Expiration Date")
    bid: Optional[str] = Field(alias="BID")
    millage_freeze_date: Optional[str] = Field(alias="Millage Freeze Date")
    millage_freeze_rate: Optional[str] = Field(alias="Millage Freeze Rate")
    veterans_exemption: Optional[str] = Field(alias="Veterans Exemption")

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


class Parcel(SanitizedBaseModel):
    """Root model containing parcel records and related address and flag information."""
    
    parcel: List[ParcelRecord] = Field(alias="Parcel")
    parcel_mailing_address: List[ParcelMailingAddressRecord] = Field(alias="Parcel Mailing Address")
    alternate_address: List[AlternateAddressRecord] = Field(alias="Alternate Address")
    act_flags: List[ActFlagsRecord] = Field(alias="ACT Flags")
    assessor: Optional[Any] = Field(None, description="Assessor information, if available. The format of this is unknown.")
    tax_collector: Optional[Any] = Field(None, description="Tax Collector information, if available. The format of this is unknown.")
    
    class Config:
        populate_by_name = True
        extra = "forbid"