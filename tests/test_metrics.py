def test_metrics_empty(client, auth_headers):
    resp = client.get("/metrics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_calls"] == 0
    assert data["booking_rate"] == 0.0


def test_metrics_with_data(client, auth_headers):
    client.post("/call-record", json={"call_id": "m1", "outcome": "booked", "sentiment": "positive", "agreed_rate": 2500, "negotiation_rounds": 2})
    client.post("/call-record", json={"call_id": "m2", "outcome": "declined", "sentiment": "negative", "negotiation_rounds": 3})
    client.post("/call-record", json={"call_id": "m3", "outcome": "booked", "sentiment": "neutral", "agreed_rate": 3000, "negotiation_rounds": 1})

    resp = client.get("/metrics", headers=auth_headers)
    data = resp.json()
    assert data["total_calls"] == 3
    assert data["booked"] == 2
    assert data["declined"] == 1
    assert data["booking_rate"] == 66.7
    assert data["avg_agreed_rate"] == 2750.0
    assert data["sentiment_positive"] == 1
    assert data["sentiment_negative"] == 1
    assert len(data["recent_calls"]) == 3


def test_metrics_requires_auth(client):
    resp = client.get("/metrics")
    assert resp.status_code == 401


def test_dashboard_serves_html(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
