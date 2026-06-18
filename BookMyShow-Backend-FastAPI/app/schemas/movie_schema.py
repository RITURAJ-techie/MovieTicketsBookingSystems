from pydantic import BaseModel,Field, ConfigDict
from typing import Optional , List
from datetime import datetime

from app.constants.enums import GenreEnum, FormatEnum, LanguageEnum
from app.schemas.artist_schema import CastCrew

class AllMovies(BaseModel):
    id: str = Field(None, alias="_id")
    title: str
    rating: str
    language: Optional[LanguageEnum] =None
    genre : Optional[GenreEnum]=None
    format : Optional[FormatEnum]=None

class Movie(BaseModel):
    title: str
    date_of_release: datetime
    duration: str
    language: LanguageEnum
    rating : str
    format: FormatEnum
    genre: GenreEnum
    about : str
    is_active : bool
    is_available: bool
    is_stream : bool = False
    price_rent: Optional[float] = None
    price_buy: Optional[float] = None
    cast: Optional[List[CastCrew]] = None
    crew: Optional[List[CastCrew]] = None

    model_config=ConfigDict(from_attributes=True)

class MovieUpdate(BaseModel):
    id:Optional[str]=None
    title: Optional[str] =None
    date_of_release: Optional[datetime] = None
    duration: Optional[str] = None
    language: Optional[LanguageEnum] =None
    rating : Optional[str] =None
    format: Optional[FormatEnum]=None
    genre: Optional[GenreEnum] =None
    about : Optional[str] = None
    is_active : Optional[bool]=None
    is_available: Optional[bool]=None
    is_stream : Optional[bool]=None
    price_rent: Optional[float] = None
    price_buy: Optional[float] = None
    cast: Optional[List[CastCrew]] = None
    crew: Optional[List[CastCrew]] = None    

class MovieDelete(BaseModel):
    message: str