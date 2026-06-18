from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone

class PromoCodeCreate(BaseModel):
    code : str 
    description : str
    discount_type : str
    discount_value : float
    max_discount : float
    min_tickets : int = 1
    start_date : datetime= datetime.now(timezone.utc)
    end_date : datetime= datetime.now(timezone.utc)
    active : bool = True

class PromoCodeResponse(PromoCodeCreate):
    promo_id : int
    model_config=ConfigDict(from_attributes=True)