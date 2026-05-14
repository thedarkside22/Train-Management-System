"""
reports_route.py - Booking Reports by Khaled (Sprint 3 - US-014)

Daily / weekly / monthly aggregates with PDF and CSV export.
"""

import csv
import io
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database import get_db
from models import Reservation, Schedule, Train, ReservationStatus
from auth import require_role


router = APIRouter(prefix="/reports", tags=["Reports"])


def _resolve_window(period: str, start: Optional[date], end: Optional[date]) -> tuple[date, date]:
    today = date.today()
    if period == "daily":
        s = start or today
        e = end or s
    elif period == "weekly":
        s = start or (today - timedelta(days=6))
        e = end or today
    elif period == "monthly":
        s = start or today.replace(day=1)
        e = end or today
    else:
        raise HTTPException(400, "period must be one of: daily, weekly, monthly")
    if s > e:
        raise HTTPException(400, "start_date must be on or before end_date")
    return s, e


def _aggregate(db: Session, start: date, end: date) -> dict:
    """Return a dict of aggregates and a daily breakdown for the window [start, end]."""
    base = db.query(Reservation).filter(
        and_(
            func.date(Reservation.booked_at) >= start,
            func.date(Reservation.booked_at) <= end,
        )
    )
    bookings = base.filter(Reservation.status == ReservationStatus.CONFIRMED).count()
    cancellations = base.filter(Reservation.status == ReservationStatus.CANCELLED).count()
    revenue = db.query(func.coalesce(func.sum(Reservation.price_paid), 0.0)).filter(
        and_(
            func.date(Reservation.booked_at) >= start,
            func.date(Reservation.booked_at) <= end,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).scalar() or 0.0

    rows = db.query(
        func.date(Reservation.booked_at).label("d"),
        func.count(Reservation.id).label("cnt"),
        func.coalesce(func.sum(Reservation.price_paid), 0.0).label("rev"),
    ).filter(
        and_(
            func.date(Reservation.booked_at) >= start,
            func.date(Reservation.booked_at) <= end,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).group_by(func.date(Reservation.booked_at)).all()

    by_day = {str(r.d): {"bookings": int(r.cnt), "revenue": float(r.rev)} for r in rows}
    days = []
    cur = start
    while cur <= end:
        key = str(cur)
        info = by_day.get(key, {"bookings": 0, "revenue": 0.0})
        days.append({"date": key, **info})
        cur += timedelta(days=1)

    # top routes
    top_routes_rows = db.query(
        Schedule.origin, Schedule.destination,
        func.count(Reservation.id).label("cnt"),
        func.coalesce(func.sum(Reservation.price_paid), 0.0).label("rev"),
    ).join(Reservation, Reservation.schedule_id == Schedule.id).filter(
        and_(
            func.date(Reservation.booked_at) >= start,
            func.date(Reservation.booked_at) <= end,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).group_by(Schedule.origin, Schedule.destination) \
     .order_by(func.count(Reservation.id).desc()).limit(5).all()

    top_routes = [
        {"origin": r[0], "destination": r[1], "bookings": int(r[2]), "revenue": float(r[3])}
        for r in top_routes_rows
    ]

    return {
        "start_date": str(start),
        "end_date": str(end),
        "total_bookings": bookings,
        "total_cancellations": cancellations,
        "total_revenue": float(revenue),
        "average_daily_revenue": float(revenue / max(1, (end - start).days + 1)),
        "by_day": days,
        "top_routes": top_routes,
    }


@router.get("/")
def generate_report(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    s, e = _resolve_window(period, start_date, end_date)
    return {"period": period, **_aggregate(db, s, e)}


@router.get("/export/csv")
def export_csv(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    s, e = _resolve_window(period, start_date, end_date)
    data = _aggregate(db, s, e)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Train Reservation System - Booking Report"])
    writer.writerow(["Period", period])
    writer.writerow(["Start", data["start_date"]])
    writer.writerow(["End", data["end_date"]])
    writer.writerow(["Total Bookings", data["total_bookings"]])
    writer.writerow(["Total Cancellations", data["total_cancellations"]])
    writer.writerow(["Total Revenue (SAR)", f"{data['total_revenue']:.2f}"])
    writer.writerow(["Avg Daily Revenue (SAR)", f"{data['average_daily_revenue']:.2f}"])
    writer.writerow([])
    writer.writerow(["Date", "Bookings", "Revenue"])
    for row in data["by_day"]:
        writer.writerow([row["date"], row["bookings"], f"{row['revenue']:.2f}"])
    writer.writerow([])
    writer.writerow(["Top Routes"])
    writer.writerow(["Origin", "Destination", "Bookings", "Revenue"])
    for r in data["top_routes"]:
        writer.writerow([r["origin"], r["destination"], r["bookings"], f"{r['revenue']:.2f}"])

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{period}_{s}_{e}.csv"},
    )


@router.get("/export/pdf")
def export_pdf(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except ImportError:
        raise HTTPException(500, "PDF generation requires reportlab. Run: pip install reportlab")

    s, e = _resolve_window(period, start_date, end_date)
    data = _aggregate(db, s, e)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Booking Report")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Train Reservation System", styles["Title"]))
    story.append(Paragraph(f"Booking Report — {period.capitalize()}", styles["Heading2"]))
    story.append(Paragraph(f"From <b>{data['start_date']}</b> to <b>{data['end_date']}</b>", styles["Normal"]))
    story.append(Spacer(1, 12))

    summary = [
        ["Metric", "Value"],
        ["Total Bookings", str(data["total_bookings"])],
        ["Total Cancellations", str(data["total_cancellations"])],
        ["Total Revenue (SAR)", f"{data['total_revenue']:.2f}"],
        ["Avg Daily Revenue (SAR)", f"{data['average_daily_revenue']:.2f}"],
    ]
    t = Table(summary, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Daily Breakdown", styles["Heading3"]))
    daily = [["Date", "Bookings", "Revenue (SAR)"]] + \
            [[d["date"], str(d["bookings"]), f"{d['revenue']:.2f}"] for d in data["by_day"]]
    t2 = Table(daily, hAlign="LEFT")
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(t2)
    story.append(Spacer(1, 18))

    if data["top_routes"]:
        story.append(Paragraph("Top Routes", styles["Heading3"]))
        rows = [["Origin", "Destination", "Bookings", "Revenue (SAR)"]]
        for r in data["top_routes"]:
            rows.append([r["origin"], r["destination"], str(r["bookings"]), f"{r['revenue']:.2f}"])
        t3 = Table(rows, hAlign="LEFT")
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#a16207")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        story.append(t3)

    story.append(Spacer(1, 18))
    story.append(Paragraph(
        f"Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        styles["Italic"],
    ))

    doc.build(story)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{period}_{s}_{e}.pdf"},
    )
