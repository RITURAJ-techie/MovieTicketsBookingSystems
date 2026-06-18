from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone

from app.schemas.seatlayout_schema import LockSeatsRequest, SeatInfo

class ConfirmBookingRequest(LockSeatsRequest):
    promo_code : Optional[str]=None
    
    model_config=ConfigDict(from_attributes=True)

class BookingResponse(BaseModel):
    booking_id: int
    total_amount: float
    seats: List[SeatInfo]
    booked_at: datetime = datetime.now(timezone.utc)
    
