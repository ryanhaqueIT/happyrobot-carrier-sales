from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.database import get_db

router = APIRouter(tags=["Webhook"])


@router.post("/webhook/happyrobot")
async def happyrobot_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("type", "")

    if event_type == "session.status_changed":
        data = payload.get("data", {})
        status = data.get("status", {}).get("current", "")
        session_id = data.get("session_id", "")
        run_id = data.get("run_id", "")

        if status == "completed":
            with get_db() as conn:
                existing = conn.execute(
                    "SELECT id FROM calls WHERE call_id = ?", (run_id,)
                ).fetchone()
                if not existing:
                    conn.execute(
                        """INSERT INTO calls (call_id, session_id, outcome, timestamp)
                           VALUES (?, ?, ?, ?)""",
                        (run_id, session_id, "completed",
                         datetime.now(timezone.utc).isoformat()),
                    )
                    conn.commit()

        return {"status": "received", "event": event_type, "session_id": session_id}

    return {"status": "ignored", "event": event_type}


@router.post("/call-record")
async def record_call(request: Request):
    body = await request.json()
    call_id = body.get("call_id", f"manual-{datetime.now(timezone.utc).timestamp()}")

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM calls WHERE call_id = ?", (call_id,)).fetchone()

        if existing:
            conn.execute(
                """UPDATE calls SET carrier_name=?, mc_number=?, equipment_type=?,
                   load_id=?, offered_rate=?, agreed_rate=?, outcome=?, sentiment=?,
                   negotiation_rounds=?, call_duration=?, transcript=?
                   WHERE call_id=?""",
                (body.get("carrier_name"), body.get("mc_number"), body.get("equipment_type"),
                 body.get("load_id"), body.get("offered_rate"), body.get("agreed_rate"),
                 body.get("outcome"), body.get("sentiment"), body.get("negotiation_rounds", 0),
                 body.get("call_duration"), body.get("transcript"), call_id),
            )
        else:
            conn.execute(
                """INSERT INTO calls (call_id, session_id, carrier_name, mc_number,
                   equipment_type, load_id, offered_rate, agreed_rate, outcome, sentiment,
                   negotiation_rounds, call_duration, transcript, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (call_id, body.get("session_id"), body.get("carrier_name"),
                 body.get("mc_number"), body.get("equipment_type"), body.get("load_id"),
                 body.get("offered_rate"), body.get("agreed_rate"), body.get("outcome"),
                 body.get("sentiment"), body.get("negotiation_rounds", 0),
                 body.get("call_duration"), body.get("transcript"),
                 datetime.now(timezone.utc).isoformat()),
            )
        conn.commit()

    return {"status": "recorded", "call_id": call_id}
