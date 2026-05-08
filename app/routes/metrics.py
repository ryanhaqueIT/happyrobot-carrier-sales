from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import require_api_key
from app.models import MetricsSummary
from app.database import get_db

router = APIRouter(tags=["Metrics"])
templates = Jinja2Templates(directory="templates")


@router.get("/metrics", response_model=MetricsSummary)
async def get_metrics(_key: str = Depends(require_api_key)):
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]

        outcomes = {}
        for row in conn.execute(
            "SELECT outcome, COUNT(*) as cnt FROM calls GROUP BY outcome"
        ).fetchall():
            outcomes[row[0] or "unknown"] = row[1]

        sentiments = {}
        for row in conn.execute(
            "SELECT sentiment, COUNT(*) as cnt FROM calls WHERE sentiment IS NOT NULL GROUP BY sentiment"
        ).fetchall():
            sentiments[row[0]] = row[1]

        avg_rate = conn.execute(
            "SELECT AVG(agreed_rate) FROM calls WHERE agreed_rate IS NOT NULL"
        ).fetchone()[0]

        avg_rounds = conn.execute(
            "SELECT AVG(negotiation_rounds) FROM calls WHERE negotiation_rounds > 0"
        ).fetchone()[0] or 0.0

        recent = conn.execute(
            """SELECT call_id, carrier_name, mc_number, equipment_type, load_id,
                      offered_rate, agreed_rate, outcome, sentiment,
                      negotiation_rounds, call_duration, timestamp
               FROM calls ORDER BY timestamp DESC LIMIT 20"""
        ).fetchall()

        booked = outcomes.get("booked", 0)

        return MetricsSummary(
            total_calls=total,
            booked=booked,
            declined=outcomes.get("declined", 0),
            not_qualified=outcomes.get("not_qualified", 0),
            no_match=outcomes.get("no_match", 0),
            transferred=outcomes.get("transferred", 0),
            dropped=outcomes.get("dropped", 0),
            booking_rate=round(booked / total * 100, 1) if total > 0 else 0.0,
            avg_agreed_rate=round(avg_rate, 2) if avg_rate else None,
            avg_negotiation_rounds=round(avg_rounds, 1),
            sentiment_positive=sentiments.get("positive", 0),
            sentiment_neutral=sentiments.get("neutral", 0),
            sentiment_negative=sentiments.get("negative", 0),
            recent_calls=[dict(row) for row in recent],
        )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")
