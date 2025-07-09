# tests/unit/test_main_handlers.py

import pytest
import json
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import main
from main import OperationRequest, http_exception_handler, validation_exception_handler

def test_operation_request_via_pydantic():
    # Invalid input should raise a Pydantic ValidationError
    with pytest.raises(ValidationError):
        OperationRequest(a="not a number", b=2)

def test_validate_numbers_raw_validator():
    # Directly exercise the raw validator path
    with pytest.raises(ValueError) as exc:
        OperationRequest.validate_numbers("foo")
    assert str(exc.value) == "Both a and b must be numbers."

@pytest.mark.anyio
async def test_http_exception_handler():
    # Simulate an HTTPException being passed to our handler
    scope = {"type": "http", "method": "GET", "path": "/foo", "headers": []}
    req = Request(scope)
    exc = HTTPException(status_code=418, detail="I'm a teapot")

    resp: JSONResponse = await http_exception_handler(req, exc)
    assert resp.status_code == 418

    body = json.loads(resp.body)
    assert body == {"error": "I'm a teapot"}

@pytest.mark.anyio
async def test_validation_exception_handler():
    # Simulate a Pydantic RequestValidationError being passed to our handler
    scope = {"type": "http", "method": "POST", "path": "/add", "headers": []}
    req = Request(scope)
    errors = [{"loc": ["body", "a"], "msg": "bad input", "type": "value_error"}]
    exc = RequestValidationError(errors)

    resp: JSONResponse = await validation_exception_handler(req, exc)
    assert resp.status_code == 400

    body = json.loads(resp.body)
    assert body == {"error": "a: bad input"}
