from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class SeatSelection(BaseModel):
    row_name: str
    seat_number: List[int]

class LockSeatsRequest(BaseModel):
    schedule_id: int
    show_id: int
    user_id: int
    seats: List[SeatSelection] = Field(..., min_length=1, max_length=10)
    locked_at: Optional[datetime] = datetime.now(timezone.utc)

class SeatInfo(BaseModel):
    row_name: str
    seat_number: int
    category: str
    price: float

