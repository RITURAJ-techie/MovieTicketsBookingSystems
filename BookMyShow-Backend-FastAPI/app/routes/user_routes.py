from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from sqlalchemy.orm import Session

from app.config.mongo_config import get_mongo_db
from app.config.postgres_config import get_db

user_router = APIRouter(prefix="/user")


# ------------------- USERS -------------------
from app.schemas.user_schema import UserLoginResponse, UserLogin,UserUpdate, UserRead
from app.services.user_service import user_login, update_user,sign_out_user

#Create/Login user
@user_router.post("/", tags=["User - Users"], response_model=UserLoginResponse)
async def create_new_user(user:UserLogin, db:Session= Depends(get_db)):
    return user_login(db, user)

from app.schemas.user_schema import UserRead
from app.services.user_service import read_user

@user_router.get("/", tags=["User - Users"],response_model=UserRead | list[UserRead])
async def get_users(
    user_id : Optional[int] = None,
    db: Session = Depends(get_db)
):
    user = read_user(db, user_id)
    if user_id is not None and not user:
        raise HTTPException(status_code=404, detail="User not found!")
    return user

#Update user
@user_router.put("/{user_id}", tags=["User - Users"], response_model=UserRead)
async def update_existing_user(user:UserUpdate, user_id:int, db: Session=Depends(get_db)):
    update_existing_user = update_user(db, user, user_id)
    if not update_existing_user:
        raise HTTPException(status_code=404, detail="User not found!")
    return update_existing_user

#User Sign Out
@user_router.delete("/{user_id}", tags=["User - Users"])
async def user_sign_out(user_id:int, db:Session = Depends(get_db)):
    delete_existing_user = sign_out_user(db,user_id)
    if delete_existing_user:
        return delete_existing_user
    raise HTTPException(status_code=404, detail="User not found")


# ------------------- MOVIES -------------------
from app.services.movie_service import get_movie_by_filter, fetch_movie_by_id
from app.services.venue_service import read_location
from app.schemas.venue_schema import LocationRead
from app.schemas.movie_schema import AllMovies, MovieUpdate

#Get available locations
@user_router.get("/explore/locations", tags=["User - Movies"], response_model=List[LocationRead]) 
async def get_locations(db:Session=Depends(get_db)):
    location = read_location(db)
    return location

#Fetch movies by location
@user_router.get("/explore/movies-{location_name}",tags=["User - Movies"], response_model=List[AllMovies])
async def get_movie_given_filters(
    location_name: str,
    language: Optional[str]=Query(None),
    genre: Optional[str]=Query(None),
    format: Optional[str]=Query(None),
    db:Session=Depends(get_db)):
    return await get_movie_by_filter(location_name, db,language, genre,format)


#Fetch movies by id -- get specific movie info
@user_router.get("/movies/{movie_id}",tags=["User - Movies"], response_model=MovieUpdate)
async def get_movie_by_id(movie_id:str):
    return await fetch_movie_by_id(movie_id)


# ------------------- SHOWS -------------------
from app.services.show_service import get_shows_by_movie_and_location , get_movieshows_for_venue

#get shows by movie name and location name
@user_router.get("/movies/{location_name}/{movie_name}/buytickets/",tags=["User - Shows"])
async def get_shows(location_name: str, movie_name: str, format:str=None, language:str=None,
                    db_pg: Session=Depends(get_db), db_mongo:Session= Depends(get_mongo_db)):
    return await get_shows_by_movie_and_location(db_pg, db_mongo, location_name,movie_name, language, format )
    
#get shows by venue name
@user_router.get("/cinemas/{location_name}/{venue_name}/buytickets/",tags=["User - Shows"])
async def get_movie_by_venue(location_name:str, venue_name:str, db:Session=Depends(get_db),db_mongo:Session=Depends(get_mongo_db)):
    res = await get_movieshows_for_venue(db, venue_name,location_name,db_mongo)
    if not res:
        raise HTTPException(status_code=404)
    return res


# ------------------- SEAT LAYOUT -------------------
from app.schemas.booking_schema import LockSeatsRequest
from app.services.seatlayout_service import lock_or_unlock_seats, seat_availability

# Seat lock 
@user_router.post("/lock",tags=["User - Seat Layout"])
def lock_seats(req: LockSeatsRequest,db: Session = Depends(get_db)):
    return lock_or_unlock_seats(db=db,schedule_id=req.schedule_id, show_id=req.show_id,
                                seats=req.seats ,lock=True)

# Seat availability
@user_router.get("/seat_layout/availability",tags=["User - Seat Layout"])
def get_seat_availability(
    show_id: int = Query(..., description="Show ID for which seat availability is needed"),
    select_seats: int = Query(1, ge=1, le=10, description="Number of seats user wants to book"),
    db: Session = Depends(get_db),
):
    return seat_availability(db, show_id=show_id, select_seats=select_seats)

# ------------------- PAYMENT -------------------
from app.schemas.payment_schema import (
    PaymentPreviewRequest,PaymentPreviewResponse,
    CancelPaymentRequest, ConfirmPaymentRequest,
    ConfirmPaymentResponse, InitiatePaymentRequest,
    InitiatePaymentResponse
)
from app.config.postgres_config import get_db
from app.services.payment_service import (
    service_payment_preview,
    service_initiate_payment,
    service_confirm_payment,
    service_cancel_payment
)

@user_router.post("/preview",tags=["User - Payment"] ,response_model=PaymentPreviewResponse)
def route_payment_preview(payload: PaymentPreviewRequest, db: Session = Depends(get_db)):
    return service_payment_preview(db, payload)


@user_router.post("/initiate", tags=["User - Payment"] ,response_model=InitiatePaymentResponse)
def route_initiate_payment(payload: InitiatePaymentRequest, db: Session = Depends(get_db)):
    return service_initiate_payment(db, payload)


@user_router.post("/confirm", tags=["User - Payment"] ,response_model=ConfirmPaymentResponse)
def route_confirm_payment(payload: ConfirmPaymentRequest, db: Session = Depends(get_db)):
    return service_confirm_payment(db, payload)


@user_router.post("/cancel",tags=["User - Payment"])
def route_cancel_payment(payload: CancelPaymentRequest, db: Session = Depends(get_db)):
    return service_cancel_payment(db, payload)

# ------------------- BOOKING -------------------
from app.services.booking_service import get_booking_info

# Get booking info 
@user_router.get("/bookings/{user_id}", tags=["User - Booking"])
async def booking_info(user_id:int, db_mongo = Depends(get_mongo_db),db:Session=Depends(get_db)):
    return await get_booking_info(db,db_mongo,user_id)

