"""
auth_routes.py - Login and Register Sprint 1 by Ziyad
POST /api/auth/register, POST /api/auth/login, GET /api/auth/me
"""


from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserRegister, UserLogin, TokenResponse, UserProfileResponse
from auth import hash_password, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserProfileResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(409, f"Username '{data.username}' already registered")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(409, f"Email '{data.email}' already registered")
    

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@router.post("/login", response_model=TokenResponse)
def login(data: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid username or password")
    if not user.is_active:
        raise HTTPException(403, "Account deactivated")
    
    token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=token, user_id=user.id,
        username=user.username, role=user.role.value,
    )



@router.get("/me", response_model=UserProfileResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user