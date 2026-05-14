# API Reference

Base URL: `http://127.0.0.1:8000/api` (dev). All endpoints (except register /
login) require `Authorization: Bearer <token>`.

> **Tip:** the live Swagger UI is always available at `/docs`, and the OpenAPI
> JSON schema at `/openapi.json`.

## Authentication

| Method | Path | Body | Role |
|--------|------|------|------|
| POST | `/auth/register` | `username, email, password, full_name, role` | public |
| POST | `/auth/login` | OAuth2 form: `username, password` | public |
| GET  | `/auth/me` | – | any authenticated |

Login returns a JWT token good for 24 hours plus the user's role.

## Trains

| Method | Path | Role |
|--------|------|------|
| POST   | `/trains/` | admin |
| GET    | `/trains/` | any |
| GET    | `/trains/{id}` | any |
| PUT    | `/trains/{id}` | admin |
| DELETE | `/trains/{id}` | admin |

`GET /trains` supports `search`, `status`, `page`, `per_page`.

## Schedules

CRUD on `/schedules/`. List supports `origin`, `destination`, `departure_date`,
`train_id`, `available_only`, `page`, `per_page`.

## Passengers

| Method | Path | Role |
|--------|------|------|
| POST | `/passengers/` | any |
| GET  | `/passengers/` | any |
| GET  | `/passengers/{id}` | any |
| GET  | `/passengers/national-id/{nid}` | any |
| **GET** | **`/passengers/{id}/bookings`** | **any (Sprint 3 - US-017)** |

The booking-history endpoint returns `passenger`, a summary
(`total_bookings, confirmed, cancelled, total_spent`) and a list of bookings
ordered most-recent first.

## Reservations

| Method | Path | Role |
|--------|------|------|
| POST | `/reservations/` | any |
| GET  | `/reservations/` | any |
| GET  | `/reservations/{id}` | any |
| GET  | `/reservations/ref/{booking_reference}` | any |
| **DELETE** | **`/reservations/{id}`** | **any (Sprint 3 - US-012)** |

### Cancellation refund schedule

| Days before departure | Refund |
|----------------------:|:------:|
| 7+ | 100 % |
| 3 – 6 | 75 % |
| 1 – 2 | 50 % |
| Same-day or past | 0 % |

The endpoint reallocates the seat (`available_seats += 1`), sets
`status=cancelled`, stamps `cancelled_at`, and returns:

```json
{
  "message": "Reservation cancelled. Seat returned to inventory.",
  "booking_reference": "TRN-AB12CD",
  "refund_amount": 75.0,
  "refund_percentage": 0.75,
  "cancelled_at": "2026-03-21T10:14:32",
  "remaining_seats": 145
}
```

## Dashboard (Sprint 3 - US-013, admin only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/stats` | trains, schedules, passengers, bookings, revenue, occupancy |
| GET | `/dashboard/revenue-trend?days=14` | daily revenue + booking count series |
| GET | `/dashboard/occupancy?limit=10` | top upcoming schedules by load factor |

The Overview tab on `/admin` polls `/dashboard/stats` every 30 s.

## Reports (Sprint 3 - US-014, admin only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reports/?period=daily|weekly|monthly&start_date=&end_date=` | JSON aggregate |
| GET | `/reports/export/csv?…` | CSV download |
| GET | `/reports/export/pdf?…` | PDF download (reportlab) |

The JSON payload exposes `total_bookings`, `total_cancellations`,
`total_revenue`, `average_daily_revenue`, a `by_day` daily breakdown, and
`top_routes` (Sprint 3 stretch).

## Analytics (Sprint 3 - US-015, admin only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/eda` | row counts, distributions, top routes, revenue summary |
| GET | `/analytics/features?limit=50` | preview of the engineered feature matrix |

Engineered columns include `dep_year, dep_month, dep_day, dep_dayofweek,
dep_is_weekend, dep_is_holiday, hour, is_morning, is_evening,
lead_time_days, occupancy_at_booking`.
