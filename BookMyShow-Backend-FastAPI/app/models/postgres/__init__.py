# base.py
from app.config.postgres_config import engine
from sqlalchemy.orm import declarative_base


Base = declarative_base()

from app.models.postgres import (
    seatlayout_model, user_model,booking_model,venue_model, show_model
)