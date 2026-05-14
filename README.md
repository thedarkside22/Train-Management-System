# Train Schedule and Reservation System

End-of-sprint-3 build of the SE1 capstone project: a full-stack train
scheduling, reservation and reporting system. Backend is FastAPI + SQLAlchemy,
frontend is React + Vite + Tailwind, and the admin dashboard ships with live
charts and exportable reports.

| Sprint | Highlights |
|-------:|------------|
| 1 | JWT auth, role-based access, Train CRUD (read/list), React shell |
| 2 | Train update/delete, schedules, passenger registration, ticket reservation, seat tracking |
| 3 | Cancellation + refunds, real-time admin dashboard, daily/weekly/monthly reports (PDF/CSV), passenger booking history, historical-booking analytics & feature engineering, full CI/CD |

## Repository layout

```
backend/                FastAPI service (Python 3.11+)
  routes/               REST endpoints grouped by domain
  analytics/            Sprint 3 data-prep / EDA / feature engineering
  tests/                pytest suite (unit + integration)
SE1-Project/            React + Vite frontend (Tailwind + Chart.js)
  src/component/        Reusable UI components
  src/pages/            Route-level pages (Login, Dashboard, AdminDashboard…)
  src/test/             Vitest tests
docs/                   API reference, user manual, deployment guide
.github/workflows/      Backend CI, Frontend CI, Integration smoke-test
```

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# API:  http://127.0.0.1:8000
# Docs: http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd SE1-Project
npm install
npm run dev
# UI: http://localhost:5173
```

### Tests

```bash
cd backend  && pytest -q             # 20+ backend tests
cd SE1-Project && npm test           # vitest API client tests
```

## Sprint 3 features at a glance

- `DELETE /api/reservations/{id}` — cancellation with seat reallocation and tiered
  refunds (100% / 75% / 50% / 0% based on lead time).
- `GET /api/dashboard/stats|revenue-trend|occupancy` — live admin metrics, used by
  the auto-refreshing **Overview** tab on `/admin`.
- `GET /api/reports/?period=daily|weekly|monthly` plus
  `GET /api/reports/export/csv|pdf` — booking reports with downloadable exports.
- `GET /api/passengers/{id}/bookings` — full booking history per passenger.
- `GET /api/analytics/eda|features` — Sprint-3 ML data-prep pipeline (collect
  → EDA → time / holiday / lead-time / occupancy features) for downstream models.

## CI/CD

- **Backend CI** — Python 3.11 & 3.12 matrix, `ruff` + `pytest`.
- **Frontend CI** — Node 20 & 22 matrix, `eslint` + `vitest` + `vite build`,
  uploads `dist/` artifact on `main`.
- **Integration** — boots the backend, hits `/health` and `/openapi.json` for a
  smoke test.

See [`docs/`](docs/) for the API reference, user manual, and deployment guide.
