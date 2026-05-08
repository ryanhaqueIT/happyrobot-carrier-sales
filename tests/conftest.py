import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_PATH"] = "test_carrier_sales.db"
os.environ["API_KEY"] = "test-key"

from app.main import app
from app.database import init_db


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    yield
    if os.path.exists("test_carrier_sales.db"):
        os.remove("test_carrier_sales.db")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}
