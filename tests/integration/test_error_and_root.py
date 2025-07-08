# tests/integration/test_error_and_root.py
import pytest
from fastapi.testclient import TestClient
import main

@pytest.fixture
def client():
    return TestClient(main.app)

def test_read_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<h1>Hello World</h1>" in r.text

def test_validation_error_add(client):
    r = client.post("/add", json={"a": "foo", "b": 2})
    assert r.status_code == 400
    # Pydantic v2 error message
    assert "a: Input should be a valid number" in r.json()["error"]

def test_subtract_internal_error(monkeypatch, client):
    monkeypatch.setattr(main, "subtract", lambda a, b: (_ for _ in ()).throw(Exception("boom")))
    r = client.post("/subtract", json={"a": 1, "b": 2})
    assert r.status_code == 400
    assert r.json() == {"error": "boom"}

def test_multiply_internal_error(monkeypatch, client):
    monkeypatch.setattr(main, "multiply", lambda a, b: (_ for _ in ()).throw(Exception("oops")))
    r = client.post("/multiply", json={"a": 1, "b": 2})
    assert r.status_code == 400
    assert r.json() == {"error": "oops"}

def test_divide_internal_error(monkeypatch, client):
    monkeypatch.setattr(main, "divide", lambda a, b: (_ for _ in ()).throw(Exception("fake")))
    r = client.post("/divide", json={"a": 1, "b": 2})
    assert r.status_code == 500
    assert r.json() == {"error": "Internal Server Error"}
