from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.seatlayout_service import lock_or_unlock_seats

from app.models.postgres.payment_model import Payment
from app.models.postgres.seatlayout_model import ShowSeatMap
from app.models.postgres.booking_model import BookingDetail
from app.models.postgres.show_model import ShowTiming, ShowSchedule
from app.services.promocode_service import validate_promocode

# Configuration
PAYMENT_TIMEOUT_MINUTES = 5
LOCK_EXPIRY_MINUTES = 10

############### HELPER ####################

def derive_category_price(layout, row_name):
    for cat in layout.get("category", []):
        if row_name in cat.get("rows", []):
            return cat["name"], cat["price"]
    raise HTTPException(status_code=400, detail=f"Row {row_name} does not exist in any category")


def release_locks_for_intent(db: Session, pi: Payment):
    lock_or_unlock_seats(db, pi.schedule_id, pi.show_id, pi.seats)


# -------------------- Service: Payment Preview --------------------
def service_payment_preview(db: Session, payload: object):
    show_timing = db.query(ShowTiming).filter(ShowTiming.show_id == payload.show_id).first()
    if not show_timing:
        raise HTTPException(status_code=404, detail="Show not found")

    schedule = db.query(ShowSchedule).filter(ShowSchedule.schedule_id == payload.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    layout = schedule.screen.seat_layout

    # compute subtotal and seat details
    total = 0.0
    seat_details = []
    for s in payload.selected_seats:
        category, price = derive_category_price(layout, s.row_name)
        for seat_number in s.seat_number:
            total += price
            seat_details.append({
                "row_name": s.row_name,
                "seat_number": seat_number,
                "category": category,
                "price": price
            })

    # validate promo (this is done at preview/intent creation time only)
    final_amount, promo_info = validate_promocode(db, payload.promo_code, payload.user_id, len(seat_details), total)

    seat_map = db.query(ShowSeatMap).filter(
        ShowSeatMap.schedule_id == payload.schedule_id,
        ShowSeatMap.show_id == payload.show_id
    ).first()

    return {
        "show": {
            "show_id": payload.show_id,
            "movie_id": schedule.movie_id,
            "venue_id": schedule.venue_id,
            "screen_id": schedule.screen_id,
            "show_date": show_timing.show_date,
            "show_time": show_timing.show_time,
            "language": show_timing.language,
            "format": show_timing.format
        },
        "selected_seats": seat_details,
        "total": total,
        "promo_applied": promo_info,
        "final_amount": final_amount,
        "locked_seats_snapshot": seat_map.locked_seats if seat_map else []
    }


# -------------------- Service: Initiate Payment (create PaymentIntent) --------------------
def normalize_selected_seats(selected_seats):
    normalized = []
    for s in selected_seats:
        for num in s.seat_number:
            normalized.append({"row_name": s.row_name, "seat_number": num})
    return normalized

def service_initiate_payment(db: Session, payload: object):
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)

    # verify seat map exists and seats locked
    seat_map = db.query(ShowSeatMap).filter(
        ShowSeatMap.schedule_id == payload.schedule_id,
        ShowSeatMap.show_id == payload.show_id
    ).first()
    if not seat_map:
        raise HTTPException(status_code=404, detail="Seat map not found")
    
    normalized_seats = normalize_selected_seats(payload.selected_seats)

    for seat in normalized_seats:
        if seat not in seat_map.locked_seats:
            raise HTTPException(
                status_code=400,
                detail=f"Seat {seat['row_name']}{seat['seat_number']} not locked"
            )

    # compute price details
    schedule = db.query(ShowSchedule).filter(ShowSchedule.schedule_id == payload.schedule_id).first()
    layout = schedule.screen.seat_layout

    total = 0.0
    seat_details = []

    for s in payload.selected_seats:
        category, price = derive_category_price(layout, s.row_name)
        for seat_number in s.seat_number:
            total += price
            seat_details.append({
                "row_name": s.row_name,
                "seat_number": seat_number,
                "category": category,
                "price": price
            })

    final_amount, promo_info = validate_promocode(db, payload.promo_code, payload.user_id, len(seat_details), total)

    # create PaymentIntent (single source of truth for amounts)
    pi = Payment(
        user_id=payload.user_id,
        schedule_id=payload.schedule_id,
        show_id=payload.show_id,
        seats=seat_details,
        original_amount=total,
        discount_amount=promo_info["discount"] if promo_info else 0,
        final_amount=final_amount,
        promo_code=promo_info["code"] if promo_info else None,
        status="pending",
        expires_at=expires_at
    )
    db.add(pi)
    db.commit()
    db.refresh(pi)

    # update lock timestamp so cleanup knows it's fresh
    seat_map.locked_at = now
    db.commit()

    return {"payment_id": pi.payment_id, "amount": pi.final_amount, "expires_at": pi.expires_at, "currency": "INR"}


# -------------------- Service: Confirm Payment (gateway calls / client confirm) --------------------
def service_confirm_payment(db: Session, payload: object):
    now = datetime.now(timezone.utc)

    # lock payment intent row for safe concurrent access
    pi = db.query(Payment).filter(Payment.payment_id == payload.payment_id).with_for_update().first()
    if not pi:
        raise HTTPException(status_code=404, detail="Payment intent not found")

    if pi.status != "pending":
        raise HTTPException(status_code=400, detail="Payment intent not in pending state")

    # check expiry
    expires_at = pi.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        pi.status = "expired"
        db.commit()
        release_locks_for_intent(db, pi)
        raise HTTPException(status_code=400, detail="Payment intent expired")

    # here we assume the payment gateway notified us of successful payment
    # (in production you should verify gateway signature / txn id)

    # fetch seat map and ensure seats still locked
    seat_map = db.query(ShowSeatMap).filter(
        ShowSeatMap.schedule_id == pi.schedule_id,
        ShowSeatMap.show_id == pi.show_id
    ).with_for_update().first()
    if not seat_map:
        raise HTTPException(status_code=404, detail="Seat map not found")
    for s in pi.seats:
        seat_obj = {"row_name": s["row_name"], "seat_number": s["seat_number"]}

        if seat_obj not in seat_map.locked_seats:
            raise HTTPException(status_code=400, detail=f"Seat {seat_obj['row_name']}{seat_obj['seat_number']} not locked")


    # Move locked -> booked and create booking atomically
    try:
        for s in pi.seats:
            seat_obj = {"row_name": s["row_name"], "seat_number": s["seat_number"]}
            if seat_obj in seat_map.locked_seats:
                seat_map.locked_seats.remove(seat_obj)
            if seat_obj not in seat_map.booked_seats:
                seat_map.booked_seats.append(seat_obj)

        # create booking
        show_timing = db.query(ShowTiming).filter(ShowTiming.show_id == pi.show_id).first()
        booking = BookingDetail(
            user_id=pi.user_id,
            schedule_id=pi.schedule_id,
            show_id=pi.show_id,
            show_date=show_timing.show_date,
            show_time=show_timing.show_time,
            language=show_timing.language,
            format=show_timing.format,
            total_amount=pi.final_amount,
            discount_amount=pi.discount_amount,
            promo_code=pi.promo_code,
            seats=pi.seats
        )
        db.add(booking)

        pi.status = "succeeded"
        db.commit()
        db.refresh(booking)

        return {"booking_id": booking.booking_id, "total_amount": booking.total_amount, "seats": booking.seats, "booked_at": booking.booked_at}

    except Exception as e:
        db.rollback()
        # revert any partials if needed
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")


# -------------------- Service: Cancel Payment --------------------
def service_cancel_payment(db: Session, payload: object):
    pi = db.query(Payment).filter(Payment.payment_id == payload.payment_id).first()
    if not pi:
        raise HTTPException(status_code=404, detail="Payment intent not found")
    if pi.status in ("succeeded", "expired"):
        raise HTTPException(status_code=400, detail="Cannot cancel")

    pi.status = "cancelled"
    db.commit()
    release_locks_for_intent(db, pi)
    return {"message": "cancelled"}