from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException

from app.models.postgres.show_model import ShowSchedule, ShowTiming
from app.schemas.show_schema import ShowScheduleCreate
from app.constants.enums import LanguageEnum,FormatEnum

############### SCHEDULE CREATE SERVICE ####################
def create_schedule(db: Session, schedule_info: ShowScheduleCreate):
    schedule = ShowSchedule(**schedule_info.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

############### MARK COMPLETED SHOWS #######################
def completed_shows(db:Session):
    current_date = datetime.now().date()
    current_time = (datetime.now()- timedelta(minutes=30)).replace(second=0, microsecond=0).time()
    
    #1. past shows --> completed
    db.query(ShowTiming).filter(
        ShowTiming.show_date < current_date,
        ShowTiming.is_active == True
    ).update({ShowTiming.is_completed:True, ShowTiming.is_active:False}, synchronize_session=False)
    
    #2. today's show, but time passed --> completed
    db.query(ShowTiming).filter(
        ShowTiming.show_date ==current_date,
        ShowTiming.show_time<current_time,
        ShowTiming.is_active == True).update({
            ShowTiming.is_active : False, ShowTiming.is_completed: True},synchronize_session=False
            )
    
    #3. activate next day
    activate_dates = [current_date+timedelta(days=i) for i in range(1,4)]

    #next_day = current_date+timedelta(days=1)
    db.query(ShowTiming).filter(
        ShowTiming.show_date.in_(activate_dates),
        ShowTiming.show_date>=current_date,
        ShowTiming.is_completed ==False).update({ShowTiming.is_active:True}, synchronize_session=False)
    
    db.commit()


############### SHOW CREATE SERVICE ####################
async def create_schedule_timings(db:Session, db_mongo, schedule_id: int, timings_info: list[ShowScheduleCreate], days_ahead :int = 10):
    completed_shows(db)

    schedule = db.query(ShowSchedule).filter(ShowSchedule.schedule_id==schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule does not exist")
    
    movie_id = schedule.movie_id
    movie_info = await db_mongo["movie_details"].find_one({"_id":ObjectId(movie_id)}, {"language":1,"format":1})
    if not movie_info:
        raise HTTPException(status_code=404, detail="Movie does not exist")
    
    allowed_languages = movie_info.get("language",[])
    allowed_formats = movie_info.get("format",[])

    today = datetime.now().date()
    timings = []

    for timing in timings_info:
        if timing.language not in allowed_languages:
            raise HTTPException(status_code=400, detail=f"Invalid language '{timing.language}'. Allowed:{allowed_languages}")
        if timing.format.value not in allowed_formats:
            raise HTTPException(status_code=400, detail=f"Invalid format '{timing.format.value}'. Allowed:{allowed_formats}")
        
        for day_offset in range(days_ahead):
            show_date = today + timedelta(days = day_offset)

            is_active = day_offset <= 2
            t = ShowTiming(
                schedule_id=schedule_id,
                show_date=show_date,
                show_time=timing.show_time,
                language=timing.language,
                format=timing.format,
                is_active=is_active,
                is_completed=False
            )
            db.add(t)
            timings.append(t)

    db.commit()
    for t in timings:
        db.refresh(t)
    return timings


############## GET LOCATION AND MOVIE INFO #################

##location_id -> location_name
def get_location_id(db_pg: Session, location_name: str) -> int:
    location_name = location_name.strip().lower()
    row = db_pg.execute(
        text("SELECT location_id FROM locations WHERE LOWER(name) = :loc"),
        {"loc": location_name}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Location not found")
    return row.location_id

##movie_id -> movie_name
async def get_movie_id(db_mongo, movie_name: str) -> str:
    movie_name = movie_name.strip().lower()
    movie_doc = await db_mongo["movie_details"].find_one(
        {"title": {"$regex": f"^{movie_name}$", "$options": "i"}},
        {"_id": 1}
    )
    if not movie_doc:
        raise HTTPException(status_code=404, detail="Movie not found")
    return str(movie_doc["_id"])

#get available language and formats
async def get_available_options(db_pg:Session, movie_id: str, location_id: int):
    completed_shows(db_pg)

    query = text("""
        SELECT DISTINCT st.format, st.language
        FROM show_timings st
        JOIN show_schedules ss ON st.schedule_id = ss.schedule_id
        JOIN venues v ON v.venue_id = ss.venue_id
        WHERE ss.movie_id = :movie_id AND v.location_id = :location_id AND st.is_active = True
""")    
    result = db_pg.execute(query, {"movie_id": movie_id, "location_id": location_id}).fetchall()

    languages = sorted(set([row.language for row in result if row.language]))
    formats = sorted(set([row.format for row in result if row.format]))

    return {
        "languages": languages,
        "formats": formats
    }

#get filtered shows info
def get_filtered_shows(db_pg:Session, movie_id:str, location_id: int, language:str= None,format:str= None):
    completed_shows(db_pg)

    base_query = """
        SELECT v.venue_name, v.venue_id, s.screen_name, s.screen_id,
               st.show_id, st.show_date, st.show_time
        FROM show_timings st
        JOIN show_schedules ss ON ss.schedule_id = st.schedule_id
        JOIN screens s ON s.screen_id = ss.screen_id
        JOIN venues v ON v.venue_id = ss.venue_id
        WHERE ss.movie_id = :movie_id 
          AND v.location_id = :location_id
          AND st.is_active = TRUE
    """

    params = {"movie_id": movie_id, "location_id": location_id}

    if language:
        base_query += " AND st.language = :language"
        params["language"] = language  

    if format:
        base_query += " AND st.format = :format"
        params["format"] = format     

    base_query += " ORDER BY v.venue_name, s.screen_name, st.show_date, st.show_time"

    rows = db_pg.execute(text(base_query), params).fetchall()

    venues = {}
    for r in rows:
        if r.venue_id not in venues:
            venues[r.venue_id] = {"venue_name": r.venue_name, "screens": {}}

        screens = venues[r.venue_id]["screens"]
        if r.screen_id not in screens:
            screens[r.screen_id] = {"screen_name": r.screen_name, "show_timings": []}

        screens[r.screen_id]["show_timings"].append({
            "show_id": r.show_id,
            "show_date": r.show_date,
            "show_time": r.show_time
        })

    return [
        {**v, "screens": list(v["screens"].values())}
        for v in venues.values()
    ]

#########################################################################  
    #     Service function: get shows by movie name and location name
#########################################################################  

async def get_shows_by_movie_and_location(db_pg: Session, db_mongo, location_name: str, movie_name: str,language:str=None, format: str = None):
    # Resolve IDs
    location_id = get_location_id(db_pg, location_name)
    movie_id = await get_movie_id(db_mongo, movie_name)

    if not format or not language:
        options = await get_available_options(db_pg, movie_id, location_id)

        if not options["formats"] and not options["languages"]:
            raise HTTPException(status_code=404, detail="No running shows")
        return {
            "movie_id": movie_id,
            "movie_name": movie_name,
            "location_name": location_name,
            "select_options": options
        }

    if language:
        language = LanguageEnum(language).value   
    if format:
        format = FormatEnum(format).value         

    show_data = get_filtered_shows(db_pg, movie_id, location_id,language, format)
    if not show_data:
        raise HTTPException(status_code=404, detail="No shows available")

    return {
        "movie_id": movie_id,
        "movie_name": movie_name,
        "location_name": location_name,
        "language":language,
        "format": format,
        "venues": show_data
    }

#########################################################################  
    #     Service function: get shows by venue name
#########################################################################  

##venue_id -> venue_name
def get_venue_id(db_pg: Session, venue_name: str) -> int:
    venue_name = venue_name.strip().lower()
    row = db_pg.execute(
        text("SELECT venue_id FROM venues WHERE LOWER(venue_name) = :loc"),
        {"loc": venue_name}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Venue not found")
    return row.venue_id

async def get_movieshows_for_venue(db:Session, venue_name:str, location_name:str, db_mongo):
    completed_shows(db)

    # fetch location_id using existing helper
    try:
        location_id = get_location_id(db, location_name)
    except HTTPException:
        return {"message": "no location found"}
    
    # fetch venue_id using existing helper
    try:
        venue_id = get_venue_id(db, venue_name)
    except HTTPException:
        return {"message": "no venue found"}

    #fetch venue info
    venue_query = text("""
        SELECT v.venue_id, v.venue_name, l.location_id, l.name
        FROM venues v
        JOIN locations l ON l.location_id = v.location_id
        WHERE v.venue_id = :venue_id AND l.location_id = :location_id
""")
    venue_info = db.execute(venue_query,{"venue_id":venue_id, "location_id":location_id}).fetchone()

    if not venue_info:
        return {"message":"No theater found"}

    #fetch show timings in the venue
    query = text("""
        SELECT ss.movie_id, st.show_id, st.show_date, st.show_time, st.language, st.format, ss.screen_id, s.screen_name
        FROM show_timings st
        JOIN show_schedules ss on ss.schedule_id = st.schedule_id
        JOIN screens s ON s.screen_id = ss.screen_id
        WHERE ss.venue_id = :venue_id
        AND st.is_active = True
        ORDER BY ss.movie_id, st.show_date, st.show_time
""")
    rows = db.execute(query, {"venue_id":venue_id}).fetchall()
    if not rows:
        return {
            "venue_id":venue_id,
            "location_id": location_id,
            "venue_name": venue_info.venue_name,
            "movies":[]
        }
    
    movies={}
    for row in rows:
        m_id = row.movie_id
        if m_id not in movies:
            movies[m_id]= {
                "screens":{}
            }

        screen_name = row.screen_name
        if screen_name not in movies[m_id]["screens"]:
            movies[m_id]["screens"][screen_name]=[]
        
        movies[m_id]["screens"][screen_name].append({
            "show_id":row.show_id,
            "show_date":row.show_date,
            "show_time":row.show_time,
            "language":row.language,
            "format":row.format
        })

    #fetch movie from mongo collection
    movie_object_ids = [ObjectId(mid) for mid in movies.keys()]
    mongo_db_movies = await db_mongo["movie_details"].find(
        {"_id": {"$in": movie_object_ids}},
        {"_id": 1, "title": 1, "language": 1, "genre": 1, "rating": 1}
    ).to_list(length=None)

    mongo_map = {str(m["_id"]): m for m in mongo_db_movies}

    res = []
    
    for movie_id, data in movies.items():
        movie_info = mongo_map.get(movie_id,{})
        res.append({
            "movie_id":movie_id,
            "title":movie_info.get("title"),
            "genre":movie_info.get("genre"),
            "rating": movie_info.get("rating"),
            "screens":[
                {"screen_name":sname,
                "show_timings":timings
                }for sname, timings in data["screens"].items()
            ]
        })

    return {
        "venue_id":venue_info.venue_id,
        "location_id":venue_info.location_id,
        "venue_name":venue_info.venue_name,
        "movies":res
    }