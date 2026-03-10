"""
passenger_route.py - Passenger Management by Azzam
POST, GET list, GET by id, GET by national_id
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math
from database import get_db
from models import Passenger
from schemas import PassengerCreate, PassengerUpdate, PassengerResponse, PaginatedResponse
from auth import get_current_user


router = APIRouter(prefix="/passengers", tags=["Passengers"])



@router.post("/", response_model=PassengerResponse, status_code=201)
def register_passenger(data: PassengerCreate, db:Session = Depends(get_db), user=Depends(get_current_user)):
    if db.query(Passenger).filter(Passenger.national_id == data.national_id).first():
        raise HTTPException(409, f"National ID '{data.national_id}' already registered")
    if data.email:
        if db.query(Passenger).filter(Passenger.email == data.email).first():
            raise HTTPException(409, f"Email '{data.email}' already registered")
    passenger = Passenger(**data.model_dump())
    db.add(passenger); db.commit(); db.refresh(passenger)
    return passenger


@router.get("/", response_model=PaginatedResponse)
def list_passengers(
    page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100),
    search:Optional[str] = None,
    db:Session = Depends(get_db), user=Depends(get_current_user)
):
    q = db.query(Passenger)
    if search:
        q = q.filter(or_(
            Passenger.full_name.ilike(f"%{search}%"),
            Passenger.national_id.ilike(f"%{search}%"),
            Passenger.phone.ilike(f"%{search}%")
        ))
    
    total = q.count()
    passengers = q.order_by(Passenger.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(
        total=total, page=page, per_page=per_page,
        total_pages=math.ceil(total/per_page) if total > 0 else 1,
        items=[PassengerResponse.model_validate(p) for p in passengers]
    )



@router.get("/{passenger_id}", response_model=PassengerResponse)
def get_passenger(passenger_id: int, db: Session=Depends(get_db), user=Depends(get_current_user)):
    p = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not p:
        raise HTTPException(404, f"Passenger {passenger_id} not found")
    return p


@router.get("/national-id/{national_id}", response_model=PassengerResponse)
def get_by_national_id(national_id: str, db: Session=Depends(get_db), user=Depends(get_current_user)):
    p = db.query(Passenger).filter(Passenger.national_id == national_id).first()
    if not p:
        raise HTTPException(404, f"No passenger with national ID '{national_id}'")
    return p
