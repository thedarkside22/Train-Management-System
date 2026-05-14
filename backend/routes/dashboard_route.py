"""
dashboard_route.py - Admin Dashboard Statistics by Khaled (Sprint 3 - US-013)

Real-time aggregate metrics: trains, schedules, passengers, bookings,
revenue, occupancy. Designed for /admin/dashboard.
"""

from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database import get_db
from models import Train, TrainStatus, Schedule, Passenger, Reservation, ReservationStatus
from schemas import DashboardStats, RevenuePoint, OccupancyPoint
from auth import require_role


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    today = date.today()
    week_ago = today - timedelta(days=7)

    total_trains = db.query(Train).count()
    active_trains = db.query(Train).filter(Train.status == TrainStatus.ACTIVE).count()
    total_schedules = db.query(Schedule).count()
    upcoming_schedules = db.query(Schedule).filter(Schedule.departure_date >= today).count()
    total_passengers = db.query(Passenger).count()

    total_reservations = db.query(Reservation).count()
    confirmed = db.query(Reservation).filter(Reservation.status == ReservationStatus.CONFIRMED).count()
    cancelled = db.query(Reservation).filter(Reservation.status == ReservationStatus.CANCELLED).count()

    bookings_today = db.query(Reservation).filter(
        and_(
            func.date(Reservation.booked_at) == today,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).count()

    revenue_today = db.query(func.coalesce(func.sum(Reservation.price_paid), 0.0)).filter(
        and_(
            func.date(Reservation.booked_at) == today,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).scalar() or 0.0

    revenue_week = db.query(func.coalesce(func.sum(Reservation.price_paid), 0.0)).filter(
        and_(
            func.date(Reservation.booked_at) >= week_ago,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).scalar() or 0.0

    revenue_total = db.query(func.coalesce(func.sum(Reservation.price_paid), 0.0)).filter(
        Reservation.status == ReservationStatus.CONFIRMED
    ).scalar() or 0.0

    # average occupancy across upcoming schedules
    occ_rows = db.query(Schedule, Train.total_seats).join(Train, Schedule.train_id == Train.id) \
        .filter(Schedule.departure_date >= today).all()
    if occ_rows:
        rates = []
        for sched, capacity in occ_rows:
            if capacity > 0:
                booked = capacity - sched.available_seats
                rates.append(booked / capacity)
        avg_occ = round(sum(rates) / len(rates), 4) if rates else 0.0
    else:
        avg_occ = 0.0

    return DashboardStats(
        total_trains=total_trains,
        active_trains=active_trains,
        total_schedules=total_schedules,
        upcoming_schedules=upcoming_schedules,
        total_passengers=total_passengers,
        total_reservations=total_reservations,
        confirmed_reservations=confirmed,
        cancelled_reservations=cancelled,
        bookings_today=bookings_today,
        revenue_today=float(revenue_today),
        revenue_this_week=float(revenue_week),
        revenue_total=float(revenue_total),
        average_occupancy=float(avg_occ),
    )


@router.get("/revenue-trend", response_model=list[RevenuePoint])
def revenue_trend(days: int = 14, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """Daily revenue points for the last N days (default 14)."""
    today = date.today()
    start = today - timedelta(days=days - 1)

    rows = db.query(
        func.date(Reservation.booked_at).label("d"),
        func.coalesce(func.sum(Reservation.price_paid), 0.0).label("rev"),
        func.count(Reservation.id).label("cnt"),
    ).filter(
        and_(
            func.date(Reservation.booked_at) >= start,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).group_by(func.date(Reservation.booked_at)).all()

    by_day = {str(r.d): (float(r.rev), int(r.cnt)) for r in rows}
    out: list[RevenuePoint] = []
    for i in range(days):
        d = start + timedelta(days=i)
        rev, cnt = by_day.get(str(d), (0.0, 0))
        out.append(RevenuePoint(label=str(d), revenue=rev, bookings=cnt))
    return out


@router.get("/occupancy", response_model=list[OccupancyPoint])
def occupancy_breakdown(limit: int = 10, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """Top upcoming schedules by occupancy rate."""
    today = date.today()
    rows = db.query(Schedule, Train).join(Train, Schedule.train_id == Train.id) \
        .filter(Schedule.departure_date >= today).all()

    points: list[OccupancyPoint] = []
    for sched, train in rows:
        if train.total_seats <= 0:
            continue
        booked = train.total_seats - sched.available_seats
        rate = round(booked / train.total_seats, 4)
        points.append(OccupancyPoint(
            schedule_id=sched.id,
            route=f"{sched.origin} → {sched.destination}",
            departure_date=str(sched.departure_date),
            occupancy_rate=rate,
            booked=booked,
            capacity=train.total_seats,
        ))
    points.sort(key=lambda p: p.occupancy_rate, reverse=True)
    return points[:limit]
