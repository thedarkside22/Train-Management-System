# User Manual

This manual walks both **staff** and **administrators** through everyday tasks.

## Logging in

1. Open the app at <http://localhost:5173>.
2. Sign in with the username + password your administrator created. Self-registration
   is also available at `/register` (defaults to the *staff* role).
3. After login the app routes you to the Dashboard. Admins see an extra
   `Admin Dashboard` link in the navbar.

## Booking a ticket (Staff)

1. From the **Dashboard** browse the list of available schedules. Use the
   filters to narrow by route or date.
2. Click **Book** on a schedule.
3. Pick a seat on the seat map (greyed seats are taken).
4. Enter passenger details (national ID, full name, phone). Returning passengers
   are recognised by national ID and reused automatically.
5. Confirm — you'll see a booking confirmation card with the reference number.

## Cancelling a booking (Sprint 3)

Two entry points:

1. **Admin Dashboard → Reservations** – click *Cancel* on the row. A confirmation
   pop-up summarises the refund. The refund schedule is automatic:

   | Days before departure | Refund |
   |----------------------:|:------:|
   | 7+                    | 100%   |
   | 3 – 6                 | 75%    |
   | 1 – 2                 | 50%    |
   | Same-day or past      | 0%     |

2. **Admin Dashboard → Booking History** – look up a passenger by national ID
   and cancel from the historical view.

The seat is automatically returned to the schedule's pool.

## Admin Dashboard tabs (Sprint 3)

* **Overview** — auto-refreshing operational metrics: revenue today / 7d /
  total, bookings today, occupancy %, charts for revenue trend and top
  schedules by load factor.
* **Trains** — create, edit, deactivate, delete trains.
* **Schedules** — manage routes, departures, ticket pricing.
* **Reservations** — list, filter by status, cancel.
* **Reports** — pick a period (daily / weekly / monthly) and optional date
  range, view aggregates and the daily breakdown, export to PDF or CSV.
* **Booking History** — passenger-level history with summary and per-booking
  cancel.
* **Analytics** — Sprint 3 EDA + engineered features (used as input for
  downstream demand-prediction models).

## Generating a report

1. Open **Admin Dashboard → Reports**.
2. Pick a period; optionally narrow by start/end date.
3. Click **Generate** – aggregates render on the page.
4. Export with **⬇ Export PDF** or **⬇ Export CSV**. The browser will start the
   download immediately.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| “Access denied. Need 'admin' role…” | logged in as staff | log out and back in as an admin |
| Charts empty on Overview | no bookings yet | book a few tickets first |
| PDF export 500s | reportlab missing | `pip install reportlab` in the backend env |
| `/admin` returns to login | token expired (24h) | log in again |
