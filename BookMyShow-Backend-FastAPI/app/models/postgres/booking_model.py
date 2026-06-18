from sqlalchemy import Column, Integer, ForeignKey, Float, String,DateTime, func, Date, Time
from sqlalchemy.dialects.postgresql import JSONB
from app.models.postgres import Base

class BookingDetail(Base):
    """
    One booking entry per user action.
    Up to 10 seats stored together.
    """
    __tablename__ = "booking_details"

    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    schedule_id = Column(Integer, ForeignKey("show_schedules.schedule_id"))
    show_id = Column(Integer, nullable=False)
    show_date = Column(Date, nullable=False)
    show_time = Column(Time, nullable=False)
    language = Column(String, nullable=False)
    format = Column(String, nullable=False)
    total_amount = Column(Float)
    discount_amount = Column(Float, default=0)
    promo_code = Column(String, nullable=True)
    booked_at = Column(DateTime, default=func.now())
    seats = Column(JSONB)  # [{row, seat_number, category, price}]
