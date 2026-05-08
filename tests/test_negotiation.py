def test_log_negotiation(client, auth_headers):
    resp = client.post(
        "/log-negotiation",
        headers=auth_headers,
        json={
            "call_id": "test-call-1",
            "round_number": 1,
            "carrier_offer": 3200,
            "agent_offer": 2800,
            "accepted": False,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "logged"
    assert data["round"] == 1


def test_log_negotiation_requires_auth(client):
    resp = client.post(
        "/log-negotiation",
        json={"call_id": "x", "round_number": 1},
    )
    assert resp.status_code == 401
