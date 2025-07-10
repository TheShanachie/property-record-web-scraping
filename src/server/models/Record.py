from recordpages.Commercial import Commercial
from recordpages.Heading import Heading
from recordpages.Homestead import Homestead
from recordpages.Land import Land
from recordpages.MultiOwner import MultiOwner
from recordpages.OutBuildings import OutBuildings
from recordpages.Owner import Owner
from recordpages.Parcel import Parcel
from recordpages.Photos import Photos
from recordpages.Residential import Residential
from recordpages.Sales import Sales
from recordpages.Values import Values

from pydantic import BaseModel, Field, ConfigDict

class Record(BaseModel):
    """Model for property record data."""
    
    heading: Heading = Field(..., description="Heading information with owner and address details")
    commercial: Commercial = Field(..., description="Commercial property details", default=None)
    homestead: Homestead = Field(..., description="Homestead exemption details", default=None)
    land: Land = Field(..., description="Land details", default=None)
    multi_owner: MultiOwner = Field(..., description="Multi-owner details", default=None)
    out_buildings: OutBuildings = Field(..., description="Outbuildings details", default=None)
    owner: Owner = Field(..., description="Owner details", default=None)
    parcel: Parcel = Field(..., description="Parcel details", default=None)
    photos: Photos = Field(..., description="Photos of the property", default=None)
    residential: Residential = Field(..., description="Residential property details", default=None)
    sales: Sales = Field(..., description="Sales history of the property", default=None)
    values: Values = Field(..., description="Property values over time", default=None)

    model_config = ConfigDict(extra='forbid')  # Forbid extra fields