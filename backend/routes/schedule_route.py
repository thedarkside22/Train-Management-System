"""
schedule_route.py - Schedule Management by Khaled
POST, GET list with filters, GET by id, PUT, DELETE
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional
from datetime import date
import math
from database import get_db
from models import Schedule, Train, TrainStatus
from schemas import ScheduleCreate, ScheduleResponse, ScheduleUpdate, PaginatedResponse
from auth import get_current_user, require_role


router = APIRouter(prefix="/schedules", tags=["Schedules"])


def _to_response(s: Schedule) -> dict:
    return ScheduleResponse(
        id=s.id, train_id=s.train_id, train_name=s.train.name, train_type=s.train.train_type,
        origin=s.origin, destination=s.destination,
        departure_date=s.departure_date, departure_time=s.departure_time, arrival_time=s.arrival_time,
        available_seats=s.available_seats, total_seats=s.train.total_seats,
        ticket_price=s.ticket_price, created_at=s.created_at
    ).model_dump()


@router.post("/", status_code=201)
def create_schedule(data: ScheduleCreate, db:Session=Depends(get_db), user=Depends(require_role("admin"))):
    train = db.query(Train).filter(Train.id == data.train_id).first()
    if not train:
        raise HTTPException(404, f"Train {data.train_id} not found")
    if train.status != TrainStatus.ACTIVE:
        raise HTTPException(400, f"Train '{train.name}' is {train.status.value}, not active")
    dup = db.query(Schedule).filter(and_(
        Schedule.train_id == data.train_id,
        Schedule.departure_date == data.departure_date,
        Schedule.departure_time == data.departure_time
    )).first()

    if dup:
        raise HTTPException(409, f"Schedule already exists for this train at that date/time")
    
    schedule = Schedule(
        train_id=train.id, origin=data.origin, destination=data.destination,
        departure_date=data.departure_date, departure_time=data.departure_time,
        arrival_time=data.arrival_time, available_seats=train.total_seats,
        ticket_price=data.ticket_price
    )
    db.add(schedule); db.commit(); db.refresh(schedule)
    return _to_response(schedule)


@router.get("/")
def list_schedules(
    origin: Optional[str] = None, destination: Optional[str] = None,
    departure_date: Optional[date] = None, train_id: Optional[int] = None,
    available_only: bool = False,
    page: int = Query(1, ge=1), per_page:int = Query(10, ge=1,le=100),
    db: Session = Depends(get_db), user=Depends(get_current_user)
):
    q = db.query(Schedule).options(joinedload(Schedule.train))
    if origin:
        q = q.filter(Schedule.origin.ilike(f"%{origin.strip()}%"))
    if destination:
        q = q.filter(Schedule.destination.ilike(f"%{destination.strip()}%"))
    if departure_date:
        q = q.filter(Schedule.departure_date == departure_date)
    if train_id:
        q = q.filter(Schedule.train_id == train_id)
    if available_only:
        q = q.filter(Schedule.available_seats > 0)
    total = q.count()
    schedules = q.order_by(Schedule.departure_date.asc(), Schedule.departure_time.asc())\
                .offset((page - 1) * per_page).limit(per_page).all()
    
    return {"total": total, "page": page, "per_page": per_page,
            "total_pages": math.ceil(total/per_page) if total > 0 else 1,
            "items": [_to_response(s) for s in schedules]}

@router.get("/{schedule_id}")
def get_schedule(schedule_id:int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.query(Schedule).options(joinedload(Schedule.train)).filter(Schedule.id == schedule_id).first()
    if not s:
        raise HTTPException(404, f"Schedule {schedule_id} not found")
    return _to_response(s)


@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, data: ScheduleUpdate, db: Session=Depends(get_db), user=Depends(require_role("admin"))):
    s = db.query(Schedule).options(joinedload(Schedule.train)).filter(Schedule.id == schedule_id).first()
    if not s:
        raise HTTPException(404, f"Schedule {schedule_id} not found")
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(400, "No fields provided")
    new_origin = update_data.get("origin", s.origin)
    new_dest = update_data.get("destination", s.destination)
    if new_origin.lower() == new_dest.lower():
        raise HTTPException(400, "Origin and destination cannot be the same")
    for field, value in update_data.items():
        setattr(s, field, value)
    db.commit(); db.refresh(s)
    return _to_response(s)


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id:int, db:Session=Depends(get_db), user=Depends(require_role("admin"))):
    s = db.query(Schedule).options(joinedload(Schedule.train)).filter(Schedule.id == schedule_id).first()
    if not s:
        raise HTTPException(404, f"Schedule {schedule_id} not found")
    info = f"{s.train.name}: {s.origin} -> {s.destination} on {s.departure_date}"
    res_count = len(s.reservations) if s.reservations else 0
    db.delete(s); db.commit()
    return {"message": "Schedule deleted", "details": info, "reservations_cancelled": res_count}

    