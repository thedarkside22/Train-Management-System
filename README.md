# Train Schedule and Reservation System

A full-stack train scheduling, reservation, and reporting system built for the
SE1 capstone project. The application supports role-based authentication, train
and schedule management, passenger reservations, cancellations, admin analytics,
and downloadable reports.

The backend is powered by FastAPI and SQLAlchemy. The frontend is a React + Vite
single-page app styled with Tailwind CSS and Chart.js.

## Features

| Area | What it includes |
|------|------------------|
| Authentication | JWT login/register flow, protected routes, role-based admin access |
| Train management | Train listing, filtering, creation, updates, deletion, and status tracking |
| Scheduling | Origin/destination/date search, schedule CRUD, and available-seat checks |
| Reservations | Passenger registration, ticket booking, booking references, and seat tracking |
| Cancellations | Seat reallocation and tiered refund calculation based on cancellation time |
| Admin dashboard | Live stats, revenue trends, occupancy charts, and operational overview |
| Reports | Daily, weekly, and monthly reports with CSV/PDF export |
| Analytics | Historical booking data preparation, EDA, and feature engineering endpoints |

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, Vite, React Router, Tailwind CSS, Chart.js |
| Backend | FastAPI, SQLAlchemy, Pydantic, Uvicorn |
| Database | SQLite for local development, PostgreSQL for deployment |
| Auth | JWT, passlib, bcrypt |
| Testing | Pytest, Vitest, React Testing Library |
| CI/CD | GitHub Actions, Render-ready deployment config |

## Repository Layout

```text
backend/                FastAPI service
  routes/               API endpoints grouped by domain
  analytics/            Data preparation, EDA, and feature engineering
  tests/                Backend pytest suite

SE1-Project/            React + Vite frontend
  src/component/        Reusable UI components
  src/pages/            Route-level pages
  src/services/         API client helpers
  src/context/          Authentication context
  src/test/             Frontend tests

docs/                   API reference, user manual, deployment guide
.github/workflows/      CI workflows
render.yaml             Render Blueprint for web, API, and PostgreSQL
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend URLs:

```text
API:  http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs
```

By default, the backend uses local SQLite:

```env
DATABASE_URL=sqlite:///./train_system.db
```

### 2. Frontend

```bash
cd SE1-Project
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

For local development, the frontend calls:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Example environment files are available at:

```text
backend/.env.example
SE1-Project/.env.example
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create a user account |
| `POST` | `/api/auth/login` | Log in and receive a JWT token |
| `GET` | `/api/auth/me` | Get the current authenticated user |
| `GET` | `/api/trains/` | List trains |
| `GET` | `/api/schedules/` | Search schedules |
| `POST` | `/api/reservations/` | Book a ticket |
| `DELETE` | `/api/reservations/{id}` | Cancel a reservation |
| `GET` | `/api/dashboard/stats` | Admin dashboard metrics |
| `GET` | `/api/reports/` | Generate booking reports |
| `GET` | `/api/analytics/eda` | Analytics summary |

See [docs/API.md](docs/API.md) for the full endpoint reference.

## Testing

Run the backend tests:

```bash
cd backend
pytest -q
```

Run the frontend tests:

```bash
cd SE1-Project
npm test
```

Build the frontend for production:

```bash
cd SE1-Project
npm run build
```

## Deployment

The project is ready for Render deployment with PostgreSQL.

Important production environment variables:

Backend service:

```env
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://your-frontend-service.onrender.com
SQL_ECHO=false
```

Frontend static site:

```env
VITE_API_BASE_URL=https://your-backend-service.onrender.com/api
```

The included [render.yaml](render.yaml) can create:

| Render resource | Purpose |
|-----------------|---------|
| `train-system-api` | FastAPI backend |
| `train-system-web` | React static frontend |
| `train-system-db` | PostgreSQL database |

After connecting a new PostgreSQL database, create/register the first admin user
again because the production database starts empty.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for more deployment details.

## Project Milestones

| Sprint | Highlights |
|-------:|------------|
| 1 | JWT authentication, role-based access, train read/list APIs, React shell |
| 2 | Train update/delete, schedules, passenger registration, ticket reservation |
| 3 | Cancellation/refunds, admin dashboard, reports, analytics, tests, CI/CD |

## Documentation

- [API Reference](docs/API.md)
- [User Manual](docs/USER_MANUAL.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Sprint 3 Notes](docs/SPRINT_3_NOTES.md)

## License

This project was developed as an academic capstone project.
