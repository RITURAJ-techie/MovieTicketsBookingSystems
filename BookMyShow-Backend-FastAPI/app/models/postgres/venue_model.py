from sqlalchemy import Column, Integer,String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.models.postgres import Base

class Location(Base):
    __tablename__= 'locations'

    location_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    venues = relationship("Venue", back_populates="location",cascade="all, delete")
    users = relationship("User", back_populates="locations")

class Venue(Base):
    __tablename__= "venues"
    venue_id = Column(Integer, primary_key=True)
    venue_name = Column(String)
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    description = Column(String)
    facilities = Column(JSONB)

    location = relationship("Location", back_populates="venues")
    screens = relationship("Screen", back_populates="venue",cascade="all, delete")
    schedules = relationship("ShowSchedule",back_populates="venue",cascade="all, delete")

class Screen(Base):
    __tablename__="screens"
    screen_id = Column(Integer, primary_key=True)
    screen_name = Column(String)
    venue_id = Column(Integer, ForeignKey("venues.venue_id"))
    seat_layout = Column(JSONB)

    venue = relationship("Venue", back_populates="screens")
    schedules = relationship("ShowSchedule",back_populates="screen",cascade="all, delete")