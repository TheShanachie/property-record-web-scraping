# from .recordpages.Commercial import Commercial
from .recordpages.Heading import Heading
from .recordpages.Homestead import Homestead
from .recordpages.Land import Land
from .recordpages.MultiOwner import MultiOwner
# from .recordpages.OutBuildings import OutBuildings
from .recordpages.Owner import Owner
from .recordpages.Parcel import Parcel
# from .recordpages.Photos import Photos
from .recordpages.Residential import Residential
from .recordpages.Sales import Sales
from .recordpages.Values import Values

from pydantic import BaseModel, Field, ConfigDict

class Record(BaseModel):
    """Model for property record data."""
    
    heading: Heading = Field(..., description="Heading information with owner and address details")
    # commercial: Commercial = Field(None, description="Commercial property details")
    homestead: Homestead = Field(None, description="Homestead exemption details")
    land: Land = Field(None, description="Land details")
    multi_owner: MultiOwner = Field(None, description="Multi-owner details")
    # out_buildings: OutBuildings = Field(None, description="Outbuildings details")
    owner: Owner = Field(None, description="Owner details")
    parcel: Parcel = Field(None, description="Parcel details")
    # photos: Photos = Field(None, description="Photos of the property")
    residential: Residential = Field(None, description="Residential property details")
    sales: Sales = Field(None, description="Sales history of the property")
    values: Values = Field(None, description="Property values over time")

    model_config = ConfigDict(extra='forbid')  # Forbid extra fields