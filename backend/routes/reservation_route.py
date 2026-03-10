"""
reservation_route.py - Ticket Booking by Ziyad
POST (book), GET list, GET by id, GET by reference
Includes seat availability logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional
import math, string, random
from database import get_db
from models import Reservation, Schedule, Passenger, ReservationStatus
from schemas import ReservationCreate, BookingConfirmation, PaginatedResponse
from auth import get_current_user


router = APIRouter(prefix="/reservations", tags=["Reservations"])


def _gen_ref() -> str:
    return "TRN-" + ''.join(random.choices(string.ascii_uppercase+string.digits, k=6))


def _reservation_dict(r) -> dict:
    return {
        "id": r.id, "booking_reference": r.booking_reference,
        "status": r.status.value, "price_paid": r.price_paid,
        "booked_at": r.booked_at.isoformat() if r.booked_at else None,
        "cancelled_at": r.cancelled_at.isoformat() if r.cancelled_at else None,
        "passenger_name": r.passenger.full_name,
        "passenger_national_id": r.passenger.national_id,
        "schedule_origin": r.schedule.origin,
        "schedule_destination": r.schedule.destination,
        "departure_date": str(r.schedule.departure_date),
        "departure_time": str(r.schedule.departure_time),
        "train_name": r.schedule.train.name,
        "remaining_seats": r.schedule.available_seats
    }


@router.post("/", response_model=BookingConfirmation, status_code=201)
def book_ticket(data: ReservationCreate, db:Session=Depends(get_db), user=Depends(get_current_user)):
    passenger = db.query(Passenger).filter(Passenger.id == data.passenger_id).first()
    if not passenger:
        raise HTTPException(404, f"Passenger {data.passenger_id} not found. Register them first.")
    

    schedule = db.query(Schedule).options(joinedload(Schedule.train))\
                .filter(Schedule.id == data.schedule_id).first()
    if not schedule:
        raise HTTPException(404, f"Schedule {data.schedule_id} not found")
    
    if schedule.available_seats <= 0:
        raise HTTPException(400, f"No seats available on {schedule.train.name}"
                            f"({schedule.origin} -> {schedule.destination})")
    
    existing = db.query(Reservation).filter(and_(
        Reservation.passenger_id == data.passenger_id,
        Reservation.schedule_id == data.schedule_id,
        Reservation.status == ReservationStatus.CONFIRMED)).first()
    if existing:
        raise HTTPException(409, f"Passenger already booked (ref: {existing.booking_reference})")
    
    try:
        ref = _gen_ref()
        while db.query(Reservation).filter(Reservation.booking_reference == ref).first():
            ref = _gen_ref()
        
        reservation = Reservation(
            passenger_id=passenger.id, schedule_id=schedule.id,
            booking_reference=ref, status=ReservationStatus.CONFIRMED,
            price_paid=schedule.ticket_price, booked_by_user_id=user.id
        )
        db.add(reservation)
        schedule.available_seats -=1
        db.commit(); db.refresh(reservation)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Booking failed: {str(e)}")
    

    return BookingConfirmation(
        message="Ticket booked successfully!",
        booking_reference=ref, passenger_name=passenger.full_name,
        train_name=schedule.train.name, origin=schedule.origin,
        destination=schedule.destination, departure_date=str(schedule.departure_date),
        departure_time=str(schedule.departure_time), price_paid=schedule.ticket_price,
        remaining_seats=schedule.available_seats
    )


@router.get("/")
def list_reservation(
    page: int = Query(1, ge=1), per_page:int =Query(10, ge=1, le=100),
    status_filter: Optional[ReservationStatus] = Query(None, alias="status"),
    passenger_id: Optional[int] = None, schedule_id: Optional[int] = None,
    db: Session = Depends(get_db), user=Depends(get_current_user)
):
    q = db.query(Reservation).options(
        joinedload(Reservation.passenger),
        joinedload(Reservation.schedule).joinedload(Schedule.train)
    )
    if status_filter:
        q = q.filter(Reservation.status == status_filter)
    if passenger_id:
        q = q.filter(Reservation.passenger_id == passenger_id)
    if schedule_id:
        q = q.filter(Reservation.schedule_id == schedule_id)
    total = q.count()
    reservations = q.order_by(Reservation.booked_at.desc())\
                   .offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page,
            "total_pages": math.ceil(total / per_page) if total > 0 else 1,
            "items": [_reservation_dict(r) for r in reservations]}


@router.get("/{reservation_id}")
def get_reservation(reservation_id: int , db:Session=Depends(get_db), user=Depends(get_current_user)):
    r = db.query(Reservation).options(
        joinedload(Reservation.passenger),
        joinedload(Reservation.schedule).joinedload(Schedule.train)
    ).filter(Reservation.id == reservation_id).first()
    if not r:
        raise HTTPException(404, f"Reservation {reservation_id} not found")
    return _reservation_dict(r)
@router.get("/ref/{booking_reference}")
def get_by_reference(booking_reference:str, db: Session=Depends(get_db), user=Depends(get_current_user)):
    r = db.query(Reservation).options(
        joinedload(Reservation.passenger),
        joinedload(Reservation.schedule).joinedload(Schedule.train)
    ).filter(Reservation.booking_reference == booking_reference).first()
    if not r:
        raise HTTPException(404, f"No reservation with reference '{booking_reference}' ")
    
    return _reservation_dict(r)


    