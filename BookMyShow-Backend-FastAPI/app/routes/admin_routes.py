from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.mongo_config import get_mongo_db
from app.config.postgres_config import get_db

admin_router = APIRouter(prefix="/admin")

# ------------------- ARTISTS -------------------
from app.schemas.artist_schema import Artist, DeleteArtist,UpdateArtist
from app.services.artist_service import create_artist, get_artists, update_artist, soft_delete_artist

#Create new artist
@admin_router.post("/artists/",tags=["Admin - Artists"],response_model=Artist)
async def create_new_artist(artist: Artist):
    return await create_artist(artist)

#Fetch artists
@admin_router.get("/artists/",tags=["Admin - Artists"], response_model=list[Artist])
async def read_all_artist():
    return await get_artists()

#Update artist details
@admin_router.patch("/artists/{artist_id}",tags=["Admin - Artists"], response_model=UpdateArtist)
async def update_artist_by_id(artist_id:str, artist: UpdateArtist):
    return await update_artist(artist_id,artist)

#Soft delete artist
@admin_router.delete("/artists/{artist_id}", tags=["Admin - Artists"], response_model=DeleteArtist)
async def delete_artist(artist_id:str):
    return await soft_delete_artist(artist_id)


# ------------------- MOVIES -------------------
from app.services.movie_service import create_movie_service, delete_movie_by_id, update_movie_by_id
from app.schemas.movie_schema import Movie, MovieDelete, MovieUpdate

#Create movie
@admin_router.post("/movies/",tags=["Admin - Movies"], response_model=Movie)
async def create_movie(movie:Movie):
    return await create_movie_service(movie)

#Update movie by id
@admin_router.patch("/movies/{movie_id}",tags=["Admin - Movies"], response_model=MovieUpdate)
async def update_movie(movie_id:str, movie:MovieUpdate):
    return await update_movie_by_id(movie_id, movie)

#Delete movie by id
@admin_router.delete("/movies/{movie_id}",tags=["Admin - Movies"], response_model=MovieDelete)
async def delete_movie(movie_id: str):
    return await delete_movie_by_id(movie_id)


# ------------------- LOCATIONS -------------------
from app.schemas.venue_schema import LocationCreate
from app.services.venue_service import create_location

#Create location
@admin_router.post("/locations/",tags=["Admin - Locations"], response_model=LocationCreate)
async def create_new_location(location:LocationCreate, db:Session=Depends(get_db)):
    return create_location(db,location)


# ------------------- VENUES -------------------
from app.schemas.venue_schema import VenueCreate 
from app.services.venue_service import create_venue 

#Create venue
@admin_router.post("/venues/",tags=["Admin - Venues"], response_model=VenueCreate)
async def create_new_venue(venue:VenueCreate, db:Session=Depends(get_db)):
    return create_venue(db,venue)


# ------------------- SCREENS -------------------
from app.schemas.venue_schema import ScreenCreate
from app.services.venue_service import create_screen

#create screen
@admin_router.post("/screens/",tags=["Admin - Screens"], response_model=ScreenCreate)
async def create_screens(screen:ScreenCreate,db: Session=Depends(get_db)):
    return create_screen(db, screen)


# ------------------- SHOWS -------------------
from app.schemas.show_schema import ShowScheduleCreate,ShowScheduleRead,ShowTimingCreate,ShowTimingRead
from app.services.show_service import create_schedule,create_schedule_timings

#create show schedule
@admin_router.post("/schedule/",tags=["Admin - Show Schedules"], response_model=ShowScheduleRead)
async def create_show_schedules(schedule:ShowScheduleCreate, db: Session= Depends(get_db)):
    return create_schedule(db,schedule)

#create show timings
@admin_router.post("/schedule/timings/", tags=["Admin - Show Timings"], response_model=list[ShowTimingRead])
async def create_timings_for_schedule(schedule_id: int,timings: list[ShowTimingCreate],days_ahead :int =10, db: Session = Depends(get_db), db_mongo = Depends(get_mongo_db)):
    return await create_schedule_timings(db, db_mongo,schedule_id, timings, days_ahead)

# ------------------- PROMOCODES -------------------
from app.schemas.promocode_schema import PromoCodeCreate ,PromoCodeResponse
from app.services.promocode_service import get_promocode, create_promocode

#Create Record
@admin_router.post("/offers/promocodes/", tags=["Admin - PromoCodes"], response_model=PromoCodeResponse)
async def create_promocodes(promocode_info:PromoCodeCreate, db:Session=Depends(get_db)):
    return create_promocode(db, promocode_info)

@admin_router.get("/offers/promocodes/", tags=["Admin - PromoCodes"], response_model=list[PromoCodeResponse])
async def get_promocode_info(db:Session=Depends(get_db)):
    return get_promocode(db)