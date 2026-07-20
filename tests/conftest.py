import pytest
from fastapi.testclient import TestClient

from app.db.seed import seed_database
from app.main import app


@pytest.fixture
def client() -> TestClient:
    seed_database()
    return TestClient(app)
