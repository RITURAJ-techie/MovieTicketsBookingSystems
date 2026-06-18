from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.postgres import Base
from sqlalchemy.ext.mutable import MutableList


class ShowSeatMap(Base):

    __tablename__ = "show_seat_mappings"

    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey("show_schedules.schedule_id"))
    show_id = Column(Integer, ForeignKey("show_timings.show_id"))
    locked_seats = Column(MutableList.as_mutable(JSONB), default=list)
    booked_seats = Column(MutableList.as_mutable(JSONB), default=list)
    locked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    schedule = relationship("ShowSchedule", back_populates="seat_map")


