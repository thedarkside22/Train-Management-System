"""
main.py - APP Entry Point by Ziyad

Sprint 1: auth + trains
Sprint 2: + passengers, schedules, reservations
Sprint 3: + cancellation, dashboard stats, reports, booking history, analytics
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.auth_routes import router as auth_router
from routes.train_routes import router as train_router
from routes.passenger_route import router as passenger_route
from routes.schedule_route import router as schedule_router
from routes.reservation_route import router as reservation_router
from routes.dashboard_route import router as dashboard_router
from routes.reports_route import router as reports_router
from routes.analytics_route import router as analytics_router


Base.metadata.create_all(bind=engine)


def get_cors_origins():
    defaults = ["http://localhost:3000", "http://localhost:5173"]
    configured = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    return defaults + [origin for origin in origins if origin not in defaults]

app = FastAPI(
    title="Train Schedule and Reservation System",
    version="0.3.0",
    description="Sprint 3 - cancellation, admin dashboard, reports, analytics, booking history.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(auth_router, prefix="/api")
app.include_router(train_router, prefix="/api")
app.include_router(passenger_route, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(reservation_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/", tags=["Health"])
def root():
    return {"system": "Train Reservation System", "sprint": 3, "status": "running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
