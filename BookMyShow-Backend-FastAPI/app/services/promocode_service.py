from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException

from app.models.postgres.pomocode_model import PromoCode
from app.schemas.promocode_schema import PromoCodeCreate, PromoCodeResponse

############### Create PromoCode Record ##############
def create_promocode(db:Session, promo_info: PromoCodeCreate):
    promo_data = PromoCode(**promo_info.model_dump())
    db.add(promo_data)
    db.commit()
    db.refresh(promo_data)
    return promo_data

############### Get PromoCode Info ##############
def get_promocode(db:Session):
    res = db.query(PromoCode).all()
    return res

############### PromoCode Validation ##############
def validate_promocode(db:Session, promo_code:str, user_id: int,seat_count: int ,total_amount: float):
    if not promo_code:
        return total_amount, None
    
    promo = db.query(PromoCode).filter(PromoCode.code == promo_code, PromoCode.active==True).first()
    if not promo:
        raise HTTPException(status_code=400, detail="Invalid promo code!")
    
    now = datetime.now(timezone.utc)
    start_date = promo.start_date
    end_date = promo.end_date

    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    if not (start_date <= now <= end_date):
        raise HTTPException(status_code=400, detail="Promo code expired or not active!")

    if seat_count < promo.min_tickets:
        raise HTTPException(status_code=400, detail=f"Minimum {promo.min_ticket} tickets required")

    # Calculate discount
    if promo.discount_type == "percentage":
        discount = total_amount * (promo.discount_value / 100)
        if promo.max_discount:
            discount = min(discount, promo.max_discount)
    else:
        discount = promo.discount_value

    new_total = total_amount - discount
    if new_total < 0:
        new_total = 0

    return new_total, {
        "code": promo.code,
        "discount": discount,
        "final_amount": new_total,
        "description": promo.description
    }