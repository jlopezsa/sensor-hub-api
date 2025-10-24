from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_ok():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_root_ok():
    res = client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert "app" in body and "message" in body
