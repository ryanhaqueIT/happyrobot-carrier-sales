from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.models import NegotiationEntry
from app.database import get_db

router = APIRouter(tags=["Negotiation"])


@router.post("/log-negotiation")
async def log_negotiation(entry: NegotiationEntry, _key: str = Depends(require_api_key)):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO negotiations (call_id, round_number, carrier_offer, agent_offer, accepted, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (entry.call_id, entry.round_number, entry.carrier_offer,
             entry.agent_offer, int(entry.accepted), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return {"status": "logged", "call_id": entry.call_id, "round": entry.round_number}
