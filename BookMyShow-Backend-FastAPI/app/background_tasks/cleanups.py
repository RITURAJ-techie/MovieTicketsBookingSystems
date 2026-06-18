import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.postgres.payment_model import Payment
from app.models.postgres.seatlayout_model import ShowSeatMap
from app.config.postgres_config import Session as SessionLocal

LOCK_EXPIRY_MINUTES = 10
PAYMENT_TIMEOUT_MINUTES = 5

async def periodic_cleanup(interval_seconds: int = 60):
    while True:
        db: Session = SessionLocal()
        try:
            now = datetime.now(timezone.utc)

            # Expire PaymentIntents that are pending and older than PAYMENT_TIMEOUT_MINUTES
            expired_threshold = now - timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
            expired_intents = db.query(Payment).filter(Payment.status == "pending", Payment.created_at <= expired_threshold).all()

            for pi in expired_intents:
                pi.status = "expired"
                # release locked seats for the intent
                seat_map = db.query(ShowSeatMap).filter( ShowSeatMap.schedule_id == pi.schedule_id,ShowSeatMap.show_id == pi.show_id).first()
                if seat_map:
                    for s in pi.seats:
                        seat_obj = {"row_name": s["row_name"], "seat_number": s["seat_number"]}
                        if seat_obj in seat_map.locked_seats:
                            seat_map.locked_seats.remove(seat_obj)
                    if not seat_map.locked_seats:
                        seat_map.locked_at = None

            db.commit()

            # Expire stale seat_map locks older than LOCK_EXPIRY_MINUTES
            stale_threshold = now - timedelta(minutes=LOCK_EXPIRY_MINUTES)
            stale_maps = db.query(ShowSeatMap).filter(ShowSeatMap.locked_at != None, ShowSeatMap.locked_at <= stale_threshold).all()
            for sm in stale_maps:
                sm.locked_seats = []
                sm.locked_at = None
            db.commit()


        except Exception:
            db.rollback()
        finally:
            db.close()
        await asyncio.sleep(interval_seconds)