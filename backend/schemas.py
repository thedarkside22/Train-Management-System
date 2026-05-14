"""
schemas.py - Request/Response validation

Sprint 1: Auth schemas by Ziyad, Train schemas by Azzam

Sprint 2: TrainUpdate by Azzam, Passenger schemas by Azzam, Schedule schemas by Khaled, Reservation schemas by Ziyad
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date, time
from enum import Enum
import re


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"


class TrainStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"



class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = Field(default= UserRole.STAFF)


    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if not re.search(r"[A-Z]",v):
            raise ValueError("Need at least one UpperCase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Need at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Need at least one digit")
        
        return v
    
    @field_validator("email")
    @classmethod
    def valid_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",v):
            raise ValueError("Invalid email format")
        return v.lower()
    

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username: only letters, numbers, underscores")
        return v.lower()



class UserLogin(BaseModel):
    username: str
    password: str



class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str



class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    model_config = {"from_attributes":True}






class TrainCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    train_type: str = Field(..., min_length=2, max_length=50)
    total_seats: int = Field(..., gt=0, le=2000)
    status: TrainStatus = Field(default=TrainStatus.ACTIVE)



class TrainUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    train_type: Optional[str] = Field(None, min_length=2, max_length=50)
    total_seats: Optional[int] = Field(None, gt=0, le=2000)
    status: Optional[TrainStatus] = None




class TrainResponse(BaseModel):
    id: int
    name: str
    train_type: str
    total_seats: int
    status: TrainStatus
    created_at: datetime
    model_config = {"from_attributes": True}




class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    items: list



class PassengerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    national_id: str = Field(..., description="Saudi national ID (10 digits)")
    email: Optional[str] = Field(None, max_length=100)
    phone: str = Field(..., description="Saudi phone: 05XXXXXXXX")


    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, v):
        cleaned = v.replace(" ", "").replace("-","")
        if not cleaned.isdigit():
            raise ValueError("National ID must be digits only")
        if len(cleaned) != 10:
            raise ValueError("National ID must be exactly 10 digits")
        if cleaned[0] not in ("1", "2"):
            raise ValueError("Must start with 1 (citizen) or 2(resident)")
        return cleaned
    

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        cleaned = v.replace(" ", "").replace("-", "")
        if cleaned.startswith("+966"):
            cleaned = "0"+ cleaned[4:]
        elif cleaned.startswith("966"):
            cleaned = "0" + cleaned[3:]
        if not re.match(r"^05\d{8}$", cleaned):
            raise ValueError("Must be a valid Saudi mobile number (05XXXXXXXX)")
        
        return cleaned
    
    @field_validator("email")
    @classmethod
    def vaildate_email(cls, v):
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        
        return v.lower()


class PassengerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = None


class PassengerResponse(BaseModel):
    id: int
    full_name: str
    national_id: str
    email: Optional[str]
    phone: str
    created_at: datetime
    model_config = {"from_attributes": True}




class ScheduleCreate(BaseModel):
    train_id: int = Field(...)
    origin: str = Field(..., min_length=2, max_length=100)
    destination: str = Field(..., min_length=2, max_length=100)
    departure_date: date = Field(...)
    departure_time: time = Field(...)
    arrival_time: time = Field(...)
    ticket_price: float = Field(..., gt=0, le=10000)


    @field_validator("origin", "destination")
    @classmethod
    def clean_city(cls,v):
        return v.strip().title()
    

    @model_validator(mode="after")
    def check_route(self):
        if self.origin and self.destination:
            if self.origin.lower() == self.destination.lower():
                raise ValueError("Origin and destination cannot be the same")
        
        return self
    


class ScheduleUpdate(BaseModel):
    origin: Optional[str] = Field(None, min_length=2,max_length=100)
    destination: Optional[str] = Field(None, min_length=2, max_length=100)
    departure_date: Optional[date] = None
    departure_time: Optional[time] = None
    arrival_time: Optional[time] = None
    ticket_price: Optional[float] = Field(None, gt=0, le=10000)


    @field_validator("origin", "destination")
    @classmethod
    def clean_city(cls, v):
        if v is None:
            return v
        return v.strip().title()



class ScheduleResponse(BaseModel):
    id: int
    train_id: int
    train_name: str
    train_type: str
    origin:str
    destination: str
    departure_date: date
    departure_time: time
    arrival_time: time
    available_seats: int
    total_seats: int
    ticket_price: float
    created_at: datetime



class ReservationCreate(BaseModel):
    passenger_id: int = Field(...)
    schedule_id: int = Field(...)


class BookingConfirmation(BaseModel):
    message: str
    booking_reference: str
    passenger_name: str
    train_name: str
    origin: str
    destination: str
    departure_date: str
    departure_time: str
    price_paid: float
    remaining_seats: int



# --------- Sprint 3 schemas ---------


class CancellationResponse(BaseModel):
    message: str
    booking_reference: str
    refund_amount: float
    refund_percentage: float
    cancelled_at: str
    remaining_seats: int


class DashboardStats(BaseModel):
    total_trains: int
    active_trains: int
    total_schedules: int
    upcoming_schedules: int
    total_passengers: int
    total_reservations: int
    confirmed_reservations: int
    cancelled_reservations: int
    bookings_today: int
    revenue_today: float
    revenue_this_week: float
    revenue_total: float
    average_occupancy: float


class RevenuePoint(BaseModel):
    label: str
    revenue: float
    bookings: int


class OccupancyPoint(BaseModel):
    schedule_id: int
    route: str
    departure_date: str
    occupancy_rate: float
    booked: int
    capacity: int


class ReportRequest(BaseModel):
    period: str = Field(..., description="daily | weekly | monthly")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
