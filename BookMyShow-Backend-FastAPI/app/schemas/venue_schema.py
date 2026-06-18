from pydantic import BaseModel, ConfigDict
from typing import Optional , List

from app.constants.enums import FacilitiesEnum

##### location #####
class LocationBase(BaseModel):
    name: str

class LocationCreate(LocationBase):
    pass

class LocationRead(LocationBase):
    location_id: Optional[int]=None

    model_config=ConfigDict(from_attributes=True)

###### venue ######
class VenueBase(BaseModel):
    venue_name : str
    location_id: int
    description : str 
    facilities: List[FacilitiesEnum]

class VenueCreate(VenueBase):
    pass

class VenueRead(VenueBase):
    venue_id:Optional[int]=None
    model_config=ConfigDict(from_attributes=True)

######### SEAT LAYOUT #########
class SeatRow(BaseModel):
    row: str
    seats : List[int]

class SeatCategory(BaseModel):
    name: str
    price: float
    rows: List[str]

class SeatLayout(BaseModel):
    rows: List[SeatRow]
    category: List[SeatCategory]

######### SCREEN #########
class ScreenBase(BaseModel):
    screen_name: str
    venue_id: int
    seat_layout: SeatLayout

class ScreenCreate(ScreenBase):
    pass

class ScreenResponse(ScreenBase):
    screen_id: int

    model_config=ConfigDict(from_attributes=True)

class VenueResponse(BaseModel):
    venue_id: int
    venue_name: str
    description: Optional[str]
    facilities: Optional[dict]
    screens: List[ScreenResponse] = [] 

    model_config=ConfigDict(from_attributes=True)

