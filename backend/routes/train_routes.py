"""
train_routes.py - Train CRUD Sprint 1 by Azzam
POST /api/trains, GET /api/trains, GET /api/trains/{id}
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math
from database import get_db
from models import Train, TrainStatus,Schedule
from schemas import TrainCreate, TrainResponse, PaginatedResponse, TrainUpdate
from auth import get_current_user, require_role


router = APIRouter(prefix="/trains", tags=["Trains"])


@router.post("/", response_model=TrainResponse, status_code=201)
def create_train(data: TrainCreate, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    if db.query(Train).filter(Train.name == data.name).first():
        raise HTTPException(409, f"Train '{data.name}' already exists")
    
    train = Train(**data.model_dump())
    db.add(train)
    db.commit()
    db.refresh(train)
    return train



@router.get("/", response_model=PaginatedResponse)
def list_trains(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[TrainStatus] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Train)
    if search:
        q = q.filter(or_(Train.name.ilike(f"%{search}%"), Train.train_type.ilike(f"%{search}%")))
    if status:
        q = q.filter(Train.status == status)
    

    total = q.count()
    trains = q.order_by(Train.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return PaginatedResponse(
        total=total, page=page, per_page=per_page,
        total_pages=math.ceil(total/per_page) if total > 0 else 1,
        items=[TrainResponse.model_validate(t) for t in trains]
    )


@router.get("/{train_id}", response_model=TrainResponse)
def get_train(train_id: int , db: Session= Depends(get_db), user=Depends(get_current_user)):
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(404, f"Train {train_id} not found")
    return train


@router.put("/{train_id}", response_model=TrainResponse)
def update_train(train_id: int, data:TrainUpdate, db:Session = Depends(get_db), user=Depends(require_role("admin"))):
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(404, f"Train {train_id} not found")
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(400, "No fields provided for update")
    if "name" in update_data and update_data["name"] != train.name:
        if db.query(Train).filter(Train.name == update_data["name"], Train.id != train_id).first():
            raise HTTPException(409, f"Train '{update_data['name']}' already exists")
    for field, value in update_data.items():
        setattr(train, field, value)
    db.commit(); db.refresh(train)
    return train


@router.delete("/{train_id}")
def delete_train(train_id: int, db:Session = Depends(get_db), user=Depends(require_role("admin"))):
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(404, f"Train {train_id} not found")
    schedule_count = db.query(Schedule).filter(Schedule.train_id == train_id).count()
    db.delete(train); db.commit()
    return {"message": f"Train '{train.name}' deleted", "deleted_schedules": schedule_count}

