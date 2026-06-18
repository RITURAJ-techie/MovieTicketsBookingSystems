from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.schemas.seatlayout_schema import SeatSelection

class PaymentPreviewRequest(BaseModel):
    user_id: int
    schedule_id: int
    show_id: int
    selected_seats: List[SeatSelection]
    promo_code: Optional[str] = None

class PaymentPreviewResponse(BaseModel):
    show: dict
    selected_seats: List[dict]
    total: float
    promo_applied: Optional[dict]
    final_amount: float
    locked_seats_snapshot: List[dict]

class InitiatePaymentRequest(PaymentPreviewRequest):
    pass

class InitiatePaymentResponse(BaseModel):
    payment_id: int
    amount: float
    expires_at: datetime
    currency: str = "INR"

class ConfirmPaymentRequest(BaseModel):
    payment_id: int
    gateway_txn_id: Optional[str] = None

class ConfirmPaymentResponse(BaseModel):
    booking_id: int
    total_amount: float
    seats: List[dict]
    booked_at: datetime

class CancelPaymentRequest(BaseModel):
    payment_id: int