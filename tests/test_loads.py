def test_search_loads_all(client, auth_headers):
    resp = client.get("/loads", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 15
    assert len(data["loads"]) == 15


def test_search_loads_by_origin(client, auth_headers):
    resp = client.get("/loads?origin=Dallas", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    for load in data["loads"]:
        assert "dallas" in load["origin"].lower()


def test_search_loads_by_equipment(client, auth_headers):
    resp = client.get("/loads?equipment_type=Reefer", headers=auth_headers)
    assert resp.status_code == 200
    for load in resp.json()["loads"]:
        assert "reefer" in load["equipment_type"].lower()


def test_get_load_by_id(client, auth_headers):
    resp = client.get("/loads/L001", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["load_id"] == "L001"


def test_get_load_not_found(client, auth_headers):
    resp = client.get("/loads/NONEXISTENT", headers=auth_headers)
    assert resp.status_code == 404


def test_loads_require_auth(client):
    resp = client.get("/loads")
    assert resp.status_code == 401
