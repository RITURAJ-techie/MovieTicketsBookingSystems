from sqlalchemy import Column, Integer, String, DateTime, Float, func
from sqlalchemy.dialects.postgresql import JSONB
from app.models.postgres import Base

class Payment(Base):
    __tablename__="payment"

    payment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    schedule_id = Column(Integer, nullable=False)
    show_id = Column(Integer, nullable=False)
    seats = Column(JSONB, nullable=False)
    original_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)
    promo_code = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, initiated, succeeded, failed, cancelled, expired
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)