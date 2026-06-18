from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from app.models.postgres import Base

class PromoCode(Base):
    __tablename__ = "promo_codes"

    promo_id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    discount_type = Column(String, nullable=False)   # 'percentage' or 'flat'
    discount_value = Column(Float, nullable=False)
    max_discount = Column(Float, nullable=True)      # e.g. 100 for TAKE100
    min_tickets = Column(Integer, default=1)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)
