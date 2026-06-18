import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.postgres.seatlayout_model import ShowSeatMap
from app.config.postgres_config import Session as SessionLocal
from app.services.seatlayout_service import LOCK_EXPIRY_MINUTES

async def auto_unlock_expired_seats():
    while True:
        try:
            db: Session = SessionLocal()
            now = datetime.now(timezone.utc)

            # Find expired locks (older than 10 minutes)
            expired_maps = db.query(ShowSeatMap).filter(
                ShowSeatMap.locked_at != None,
                now - ShowSeatMap.locked_at > timedelta(minutes=LOCK_EXPIRY_MINUTES)
            ).all()

            for seat_map in expired_maps:
                seat_map.locked_seats = []
                seat_map.locked_at = None
                print(f"[AUTO-UNLOCK] Released expired seats for show {seat_map.show_id}")

            db.commit()
            db.close()

        except Exception as e:
            print(f"[AUTO-UNLOCK] Error: {e}")

        await asyncio.sleep(60)


########### FastAPI BackgroundScheduler###########

from apscheduler.schedulers.background import BackgroundScheduler
from app.background_tasks.auto_unlock import auto_unlock_expired_seats
from app.services.show_service import completed_shows

### Auto unlock expired seats
def start_scheduler():
    scheduler = BackgroundScheduler()

    def job():
        db = SessionLocal()
        try:
            auto_unlock_expired_seats(db)
        finally:
            db.close()

    scheduler.add_job(job, "interval", minutes=1)
    scheduler.start()

### Update completed shows
def run_completed_shows():
    db = SessionLocal()
    try:
        completed_shows(db)
    finally:
        db.close()
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_completed_shows, 'interval', minutes = 15)
    scheduler.start()