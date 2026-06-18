from sqlalchemy import Column, Integer, String, Boolean,ForeignKey, Date, Time,Enum
from sqlalchemy.orm import relationship
from app.constants.enums import LanguageEnum,FormatEnum

from app.models.postgres import Base

class ShowSchedule(Base):
    __tablename__="show_schedules"

    schedule_id = Column(Integer,primary_key=True)
    movie_id = Column(String, index=True)
    screen_id = Column(Integer, ForeignKey("screens.screen_id"))
    venue_id = Column(Integer, ForeignKey("venues.venue_id"))

    screen = relationship("Screen",back_populates="schedules")
    venue = relationship("Venue",back_populates="schedules")
    timings = relationship("ShowTiming", back_populates="schedule",cascade="all, delete")
    seat_map = relationship("ShowSeatMap", back_populates="schedule", uselist=False, cascade="all, delete")


class ShowTiming(Base):
    __tablename__="show_timings"

    show_id = Column(Integer,primary_key=True)
    schedule_id = Column(Integer,ForeignKey("show_schedules.schedule_id"))
    language = Column(Enum(LanguageEnum))
    format = Column(Enum(FormatEnum, values_callable=lambda x: [e.value for e in x]),nullable=False)
    show_date = Column(Date)
    show_time = Column(Time)
    is_active = Column(Boolean,default=True)
    is_completed = Column(Boolean,default=False)

    schedule = relationship("ShowSchedule",back_populates="timings")

