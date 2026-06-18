from sqlalchemy.orm import Session
from sqlalchemy import text
from bson import ObjectId

from app.services.seatlayout_service import LOCK_EXPIRY_MINUTES

############### GET BOOKING INFO SERVICE ####################

async def get_booking_info(db: Session, db_mongo, user_id: int):
    query = text("""
        SELECT b.booking_id, b.user_id, b.schedule_id, 
            b.show_date, b.show_time, b.language, b.format, b.total_amount,
            b.seats, b.booked_at,
            ss.movie_id, ss.venue_id, ss.screen_id,v.venue_name, s.screen_name
        FROM booking_details b
        JOIN show_schedules ss on ss.schedule_id = b.schedule_id
        JOIN venues v on v.venue_id = ss.venue_id
        JOIN screens s on s.screen_id = ss.screen_id
        WHERE b.user_id = :user_id
        ORDER BY b.booked_at DESC
""")

    result = db.execute(query, {"user_id": user_id}).fetchall()
    if not result:
        return []
    
    movie_id = [r.movie_id for r in result if r.movie_id]
    object_ids = [ObjectId(m_id) for m_id in movie_id if ObjectId.is_valid(m_id)]
    
    mongo_movie_list  = await db_mongo["movie_details"].find(
        {"_id": {"$in": object_ids}}, {"_id": 1, "title": 1}
    ).to_list(length=None)

    movie_map = {str(m["_id"]): m["title"] for m in mongo_movie_list}
    return [
        {
            "booking_id": r.booking_id,
            "user_id": r.user_id,
            "movie_name": movie_map.get(r.movie_id),
            "language": r.language,
            "format": r.format,
            "venue_name": r.venue_name,
            "screen_name": r.screen_name,
            "show_date": r.show_date,
            "show_time": r.show_time,
            "seats": r.seats,
            "total_amount": r.total_amount,
            "booked_at": r.booked_at,            
        }

        for r in result
    ]