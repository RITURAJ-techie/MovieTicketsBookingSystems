from pydantic import BaseModel, Field
from typing import Optional, List

from app.constants.enums import OccupationEnum

######### Cast and Crew in Movie detail ########
class CastCrew(BaseModel):
    id : Optional[str] = Field(None,alias="_id")
    role: Optional[str]=None

######### Artist details ########
class Artist(BaseModel):
    name : str
    occupation : List[OccupationEnum]
    also_known : Optional[str] = None
    birthplace : str
    children: Optional[int] = None #count of children
    about : str
    spouse : Optional[str] = None
    family : Optional[List[CastCrew]] = None  
    peer_and_more : Optional[List[CastCrew]] = None
    is_available: bool = True

class UpdateArtist(BaseModel):
    id:Optional[str]=None
    name : Optional[str] = None
    occupation : Optional[List[OccupationEnum]] = None
    also_known : Optional[str] = None
    birthplace : Optional[str] = None
    children: Optional[int] = None #count of children
    about : Optional[str] = None
    spouse : Optional[str] = None
    family : Optional[List[CastCrew]] = None  
    peer_and_more : Optional[List[CastCrew]] = None  

class DeleteArtist(BaseModel):
    message: str
