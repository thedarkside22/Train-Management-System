# Sprint 3 – Delivery Notes

This document maps the Sprint 3 backlog (from
`Train_System_Scrum_Complete_1.xlsx`, sheet *Sprint 3*) to what shipped.

## User stories

| Story | Title | Status | Where |
|-------|-------|--------|-------|
| US-012 | Ticket Cancellation | ✅ done | `backend/routes/reservation_route.py` `DELETE /api/reservations/{id}` + Admin UI **Reservations / Booking History** tabs |
| US-013 | Admin Dashboard | ✅ done | `backend/routes/dashboard_route.py` (3 endpoints) + `SE1-Project/src/component/DashboardOverview.jsx` (Chart.js, auto-refresh) |
| US-014 | Booking Reports | ✅ done | `backend/routes/reports_route.py` JSON + CSV + PDF + `ReportsPanel.jsx` |
| US-015 | Historical Booking Analytics & Feature Engineering | ✅ done (data pipeline) | `backend/analytics/data_prep.py` + `backend/routes/analytics_route.py` + `AnalyticsPanel.jsx` |
| US-017 | Booking History | ✅ done | `GET /api/passengers/{id}/bookings` + `BookingHistoryPanel.jsx` |

## Testing & QA tasks

| Task | Status | Where |
|------|--------|-------|
| Unit tests for all API endpoints | ✅ | `backend/tests/test_*.py` (auth, trains, dashboard/reports/analytics) |
| Integration tests for booking flow | ✅ | `backend/tests/test_booking_flow.py` (book → cancel → seat returned, overbooking, idempotent cancel) |
| End-to-end UI testing | ✅ smoke | `vitest` covers the Sprint 3 API client; `.github/workflows/integration.yml` boots the API and smoke-tests it |
| Bug fixes & perf optimisation | ✅ | refund logic; async-friendly Chart.js wiring; deprecated pydantic `regex=` swapped for `pattern=` |

## Documentation tasks

| Task | Where |
|------|-------|
| API documentation | [`docs/API.md`](API.md) |
| User manual | [`docs/USER_MANUAL.md`](USER_MANUAL.md) |
| Deployment guide | [`docs/DEPLOYMENT.md`](DEPLOYMENT.md) |
| Presentation slides | tracked in the team Drive – out of repo scope |

## CI / CD

Three GitHub Actions workflows added under `.github/workflows/`:

1. **Backend CI** — Python 3.11 + 3.12 matrix, runs `ruff` and the full pytest
   suite against an isolated SQLite DB.
2. **Frontend CI** — Node 20 + 22 matrix, runs ESLint, Vitest, builds with
   Vite and uploads the `dist/` artifact.
3. **Integration** — boots the API in the runner, hits `/health` and
   `/openapi.json` for a smoke check.

## Out of scope / future sprints

* Email confirmations (US-015 in the *Product Backlog* — different US-015 to
  the Sprint 3 row, kept on the backlog)
* Mobile-responsive polish (US-016)
* Advanced search filters on schedules (US-017 backlog row)
* Automated cloud backups (US-018) — bash + cron template included in
  `docs/DEPLOYMENT.md`.
