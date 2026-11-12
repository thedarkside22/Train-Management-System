"""
models.py databse models
Khaled's file. defines user and train tables

Sprint 1: User, Train
Sprint 2: Schedule, Passenger, Reservation
"""


from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, Date, Time, CheckConstraint, UniqueConstraint

from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from database import Base
from encryption import EncryptedString, blind_index
import enum



class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"


class TrainStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class ReservationStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STAFF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class Train(Base):
    __tablename__ = "trains"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    train_type = Column(String(50), nullable=False)
    total_seats = Column(Integer, nullable=False)
    status = Column(Enum(TrainStatus), nullable=False,default=TrainStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    schedules = relationship("Schedule", back_populates="train", cascade="all, delete-orphan")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    train_id = Column(Integer, ForeignKey("trains.id", ondelete="CASCADE"), nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    departure_date = Column(Date , nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    available_seats = Column(Integer, nullable=False)
    ticket_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    train = relationship("Train", back_populates="schedules")
    reservations = relationship("Reservation", back_populates="schedule", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("available_seats >=0", name="check_seats_non_negative"),
        CheckConstraint("ticket_price > 0", name="check_price_positive")
    )



class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    passenger_id = Column(Integer,ForeignKey("passengers.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    booking_reference = Column(String(20), unique=True, nullable=False, index=True)
    status = Column(Enum(ReservationStatus), nullable=False, default=ReservationStatus.CONFIRMED)
    price_paid = Column(Float, nullable=False)
    booked_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booked_at = Column(DateTime(timezone=True), server_default=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    passenger = relationship("Passenger", back_populates="reservations")
    schedule = relationship("Schedule", back_populates="reservations")
    __table_args__ = (
        UniqueConstraint("passenger_id", "schedule_id", name="unique_passenger_schedule"),
    )


class Passenger(Base):
    __tablename__ = "passengers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)

    # Personal data is encrypted at rest (see encryption.py). Each encrypted
    # column has a "*_hash" blind index for exact lookups and uniqueness,
    # because ciphertext itself cannot be searched.
    national_id = Column(EncryptedString, nullable=False)
    national_id_hash = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(EncryptedString, nullable=True)
    email_hash = Column(String(64), unique=True, nullable=True, index=True)
    phone = Column(EncryptedString, nullable=False)
    phone_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reservations = relationship("Reservation", back_populates="passenger")

    @validates("national_id", "email", "phone")
    def _keep_blind_index_in_sync(self, field, value):
        setattr(self, f"{field}_hash", None if value is None else blind_index(field, value))
        return value
 