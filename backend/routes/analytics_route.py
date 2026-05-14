"""
analytics_route.py - Historical booking analytics by Ziyad (Sprint 3 - US-015)

Wraps analytics.data_prep so admins can pull EDA + feature snapshots from the API.
Heavy ML training is intentionally out of scope; this exposes the pipeline output.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth import require_role
from analytics.data_prep import collect_bookings, exploratory_analysis, feature_engineering


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/eda")
def eda(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """Exploratory analysis summary of historical bookings."""
    df = collect_bookings(db)
    return exploratory_analysis(df)


@router.get("/features")
def features(limit: int = 50, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """A preview of the engineered feature set (ready for downstream ML)."""
    df = collect_bookings(db)
    feat = feature_engineering(df)
    if feat.empty:
        return {"rows": 0, "columns": [], "preview": []}
    preview = feat.head(limit).to_dict(orient="records")
    # ensure JSON serialisable (dates -> str)
    for row in preview:
        for k, v in list(row.items()):
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
    return {
        "rows": int(len(feat)),
        "columns": list(feat.columns),
        "preview": preview,
    }
