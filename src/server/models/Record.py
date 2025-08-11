# from .recordpages.Commercial import Commercial
from .recordpages.Heading import Heading
from .recordpages.Homestead import Homestead
from .recordpages.Land import Land
from .recordpages.MultiOwner import MultiOwner
# from .recordpages.OutBuildings import OutBuildings
from .recordpages.Owner import Owner
from .SanitizeMixin import SanitizedBaseModel
from .recordpages.Parcel import Parcel
# from .recordpages.Photos import Photos
from .recordpages.Residential import Residential
from .recordpages.Sales import Sales
from .recordpages.Values import Values
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class PageData(SanitizedBaseModel):
    # Non Case sensitive fields
    model_config = ConfigDict(case_insensitive=True)
    
    # commercial: Optional[Commercial] = Field(None, description="Commercial property details")
    homestead: Optional[Homestead] = Field(None, description="Homestead exemption details")
    land: Optional[Land] = Field(None, description="Land details")
    multi_owner: Optional[MultiOwner] = Field(None, description="Multi-owner details")
    # out_buildings: Optional[OutBuildings] = Field(None, description="Outbuildings details")
    owner: Optional[Owner] = Field(None, description="Owner details")
    parcel: Optional[Parcel] = Field(None, description="Parcel details")
    # photos: Optional[Photos] = Field(None, description="Photos of the property")
    residential: Optional[Residential] = Field(None, description="Residential property details")
    sales: Optional[Sales] = Field(None, description="Sales history of the property")
    values: Optional[Values] = Field(None, description="Property values over time") 

class Record(SanitizedBaseModel):
    """Model for property record data."""
    
    heading: Heading = Field(..., description="Heading information with owner and address details")
    page_data: PageData = Field(..., description="Detailed property information across multiple pages") 
    

    model_config = ConfigDict(extra='forbid')  # Forbid extra fields