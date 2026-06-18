from sqlalchemy.orm import Session

from app.models.postgres.venue_model import Location, Venue, Screen
from app.schemas.venue_schema import LocationCreate, VenueCreate, ScreenCreate

########### Location #############
def create_location(db:Session, data:LocationCreate):
    location = Location(**data.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

def read_location(db:Session, location_id :int | None = None):
    query = db.query(Location)
    if location_id:
        return query.filter(Location.location_id == location_id).first()
    return query.all()

########### Venue #############
def create_venue(db:Session, data:VenueCreate):
    venue = Venue(**data.model_dump())
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue

def read_venue(db:Session, venue_id :int | None = None):
    query = db.query(Venue)
    if venue_id:
        return query.filter(Venue.venue_id == venue_id).first()
    return query.all()

########### Screen #############
def create_screen(db:Session, data:ScreenCreate) -> Screen:
    screen_dict = data.model_dump()
    screen = Screen(**screen_dict)
    db.add(screen)
    db.commit()
    db.refresh(screen)
    return screen

def read_screen(db:Session, screen_id :int | None = None):
    query = db.query(Screen)
    if screen_id:
        return query.filter(Screen.screen_id == screen_id)#.first()
    return query.all()
