"""
data_prep.py - Historical booking data preprocessing (Sprint 3 - US-015) by Ziyad.

Three responsibilities:
1. collect_bookings(db) - pull raw historical bookings into a DataFrame
2. exploratory_analysis(df) - basic EDA (counts, distributions, summary stats)
3. feature_engineering(df) - time-based + holiday features ready for an ML model

This module is dependency-light and does not perform any model training - it
prepares the dataset that downstream sprints (or a notebook) can consume.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

import pandas as pd
from sqlalchemy.orm import Session

from models import Reservation, Schedule, Train, Passenger


# Saudi national / commonly observed holidays for feature flagging
SAUDI_HOLIDAYS_MMDD: set[str] = {
    "02-22",  # Founding Day
    "09-23",  # National Day
}


def collect_bookings(db: Session) -> pd.DataFrame:
    """Join Reservation -> Schedule -> Train -> Passenger and return as DataFrame."""
    rows = (
        db.query(Reservation, Schedule, Train, Passenger)
        .join(Schedule, Reservation.schedule_id == Schedule.id)
        .join(Train, Schedule.train_id == Train.id)
        .join(Passenger, Reservation.passenger_id == Passenger.id)
        .all()
    )

    records = []
    for r, s, t, p in rows:
        records.append({
            "reservation_id": r.id,
            "booking_reference": r.booking_reference,
            "status": r.status.value,
            "price_paid": float(r.price_paid),
            "booked_at": r.booked_at,
            "cancelled_at": r.cancelled_at,
            "schedule_id": s.id,
            "origin": s.origin,
            "destination": s.destination,
            "departure_date": s.departure_date,
            "departure_time": str(s.departure_time),
            "available_seats_at_query": s.available_seats,
            "train_id": t.id,
            "train_name": t.name,
            "train_type": t.train_type,
            "train_capacity": t.total_seats,
            "passenger_id": p.id,
        })
    return pd.DataFrame.from_records(records)


def exploratory_analysis(df: pd.DataFrame) -> dict:
    """Return a JSON-serialisable summary describing the dataset."""
    if df.empty:
        return {"rows": 0, "note": "no booking history yet"}

    by_status = df["status"].value_counts().to_dict()
    by_route = (
        df.groupby(["origin", "destination"])
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="bookings")
        .to_dict(orient="records")
    )
    by_train_type = df["train_type"].value_counts().to_dict()
    revenue = float(df.loc[df["status"] == "confirmed", "price_paid"].sum())

    return {
        "rows": int(len(df)),
        "unique_passengers": int(df["passenger_id"].nunique()),
        "unique_routes": int(df.groupby(["origin", "destination"]).ngroups),
        "by_status": {str(k): int(v) for k, v in by_status.items()},
        "by_train_type": {str(k): int(v) for k, v in by_train_type.items()},
        "top_routes": by_route,
        "total_revenue": revenue,
        "price_min": float(df["price_paid"].min()),
        "price_max": float(df["price_paid"].max()),
        "price_mean": float(df["price_paid"].mean()),
    }


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer time-based and holiday features.

    Adds:
        - dep_year, dep_month, dep_day, dep_dayofweek
        - dep_is_weekend, dep_is_holiday
        - hour, is_morning, is_evening
        - lead_time_days (days between booking and departure)
        - occupancy_at_booking (capacity utilisation snapshot)
    """
    if df.empty:
        return df.copy()

    out = df.copy()
    dep = pd.to_datetime(out["departure_date"])
    out["dep_year"] = dep.dt.year
    out["dep_month"] = dep.dt.month
    out["dep_day"] = dep.dt.day
    out["dep_dayofweek"] = dep.dt.dayofweek  # 0 = Mon
    out["dep_is_weekend"] = out["dep_dayofweek"].isin([4, 5]).astype(int)  # Fri/Sat in KSA
    out["dep_is_holiday"] = dep.dt.strftime("%m-%d").isin(SAUDI_HOLIDAYS_MMDD).astype(int)

    hour = pd.to_datetime(out["departure_time"], format="%H:%M:%S", errors="coerce").dt.hour.fillna(0).astype(int)
    out["hour"] = hour
    out["is_morning"] = ((hour >= 5) & (hour < 12)).astype(int)
    out["is_evening"] = ((hour >= 17) & (hour < 22)).astype(int)

    booked_at = pd.to_datetime(out["booked_at"]).dt.tz_localize(None) if out["booked_at"].notna().any() else pd.NaT
    out["lead_time_days"] = (dep - booked_at).dt.days

    capacity = out["train_capacity"].replace(0, pd.NA)
    booked = capacity - out["available_seats_at_query"]
    out["occupancy_at_booking"] = (booked / capacity).astype(float).fillna(0.0).clip(0.0, 1.0)

    return out


def build_dataset(db: Session) -> tuple[pd.DataFrame, dict]:
    """One-call helper: collect → EDA → feature engineering."""
    raw = collect_bookings(db)
    eda = exploratory_analysis(raw)
    features = feature_engineering(raw)
    return features, eda
