# tests/integration/test_error_and_root.py

import pytest
from fastapi.testclient import TestClient
import app.operations as ops
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_read_root(client):
    r = client.get("/")
    assert r.status_code == 200
    # Jinja2Templates returns HTML
    assert "text/html" in r.headers["content-type"]
    assert "<h1>Hello World</h1>" in r.text

def test_validation_error_add(client):
    # non‐numeric a triggers our validation_exception_handler
    r = client.post("/add", json={"a": "foo", "b": 2})
    assert r.status_code == 400
    body = r.json()
    assert "error" in body
    assert "a: value is not a valid float" in body["error"]

def test_subtract_internal_error(monkeypatch, client):
    # force subtract to blow up
    monkeypatch.setattr(ops, "subtract", lambda a, b: (_ for _ in ()).throw(Exception("boom")))
    r = client.post("/subtract", json={"a": 1, "b": 2})
    assert r.status_code == 400
    assert r.json() == {"error": "boom"}

def test_multiply_internal_error(monkeypatch, client):
    monkeypatch.setattr(ops, "multiply", lambda a, b: (_ for _ in ()).throw(Exception("oops")))
    r = client.post("/multiply", json={"a": 1, "b": 2})
    assert r.status_code == 400
    assert r.json() == {"error": "oops"}

def test_divide_internal_error(monkeypatch, client):
    monkeypatch.setattr(ops, "divide", lambda a, b: (_ for _ in ()).throw(Exception("fake")))
    r = client.post("/divide", json={"a": 1, "b": 2})
    assert r.status_code == 500
    assert r.json() == {"error": "Internal Server Error"}
