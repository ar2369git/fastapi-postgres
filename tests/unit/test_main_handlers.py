# tests/unit/test_main_handlers.py

import pytest
import json
import asyncio
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.requests import Request
from fastapi.responses import JSONResponse
import main
from main import OperationRequest, http_exception_handler, validation_exception_handler
from pydantic import ValidationError

def test_operation_request_via_pydantic():
    # constructing with invalid input should raise Pydantic ValidationError
    with pytest.raises(ValidationError):
        OperationRequest(a="not a number", b=2)

def test_validate_numbers_raw_validator():
    # directly exercise the raw validator path
    with pytest.raises(ValueError) as exc:
        OperationRequest.validate_numbers("foo")
    assert str(exc.value) == "Both a and b must be numbers."

def test_http_exception_handler():
    # simulate an HTTPException being passed to our handler
    scope = {"type": "http", "method": "GET", "path": "/foo", "headers": []}
    req = Request(scope)
    exc = HTTPException(status_code=418, detail="I'm a teapot")

    # run the async handler in its own loop
    resp: JSONResponse = asyncio.run(http_exception_handler(req, exc))
    assert resp.status_code == 418

    body = json.loads(resp.body)
    assert body == {"error": "I'm a teapot"}

def test_validation_exception_handler():
    # simulate a Pydantic RequestValidationError being passed to our handler
    scope = {"type": "http", "method": "POST", "path": "/add", "headers": []}
    req = Request(scope)
    errors = [{"loc": ["body", "a"], "msg": "bad input", "type": "value_error"}]
    exc = RequestValidationError(errors)

    resp: JSONResponse = asyncio.run(validation_exception_handler(req, exc))
    assert resp.status_code == 400

    body = json.loads(resp.body)
    assert body == {"error": "a: bad input"}
