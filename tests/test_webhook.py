def test_webhook_session_completed(client):
    resp = client.post(
        "/webhook/happyrobot",
        json={
            "type": "session.status_changed",
            "data": {
                "run_id": "run-webhook-test",
                "session_id": "sess-123",
                "status": {"previous": "in-progress", "current": "completed"},
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "received"


def test_webhook_ignores_unknown_events(client):
    resp = client.post(
        "/webhook/happyrobot",
        json={"type": "some.other.event", "data": {}},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_call_record_create(client):
    resp = client.post(
        "/call-record",
        json={
            "call_id": "rec-test-1",
            "carrier_name": "Test Trucking",
            "mc_number": "123456",
            "outcome": "booked",
            "sentiment": "positive",
            "agreed_rate": 2500,
            "negotiation_rounds": 2,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"


def test_call_record_update(client):
    client.post("/call-record", json={"call_id": "rec-update-1", "outcome": "completed"})
    resp = client.post(
        "/call-record",
        json={"call_id": "rec-update-1", "outcome": "booked", "agreed_rate": 3000},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"
