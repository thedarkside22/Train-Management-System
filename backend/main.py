"""
main.py - APP Entry Point by Ziyad

Sprint 1: auth + trains
Sprint 2: + passengers, schedules, reservations
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.auth_routes import router as auth_router
from routes.train_routes import router as train_router
from routes.passenger_route import router as passenger_route
from routes.schedule_route import router as schedule_router
from routes.reservation_route import router as reservation_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Train Schedule and Reservation System",
    version="0.2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(auth_router, prefix="/api")
app.include_router(train_router, prefix="/api")
app.include_router(passenger_route, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(reservation_router, prefix="/api")


@app.get("/", tags=["Health"])
def root():
    return {"system": "Train Reservation System", "sprint": 2, "status":"running"}