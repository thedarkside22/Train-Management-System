"""
auth.py - Authentication System Sprint 1 - Ziyad
Password hashing, JWT tokens, and role checking.
"""

from datetime import datetime, timedelta,timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from models import User


SECRET_KEY = "6733f17dd5dfb3556969e21d544bc1c2e50cab07667e5093c09c4af49afd3709"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


pwd_context = CryptContext(schemes=["bcrypt", "sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain:str, hashed:str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data:dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)) -> User:

    cred_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expire token", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise cred_error
    except InvalidTokenError:
        raise cred_error
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise cred_error
    if not user.is_active:
        raise cred_error
    return user




def require_role(role: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value != role:
            raise HTTPException(status_code=403, detail=f"Access denied. Need '{role}' role to access, you have {current_user.role.value}")
        
        return current_user
    return checker



