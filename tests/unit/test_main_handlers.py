# tests/unit/test_main_handlers.py

import pytest
import json
import asyncio
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

def test_http_exception_handler():
    # Simulate raising an HTTPException
    scope = {"type": "http", "method": "GET", "path": "/foo", "headers": []}
    req = Request(scope)
    exc = HTTPException(status_code=418, detail="I'm a teapot")

    # Run the async handler on its own new loop
    loop = asyncio.new_event_loop()
    try:
        resp: JSONResponse = loop.run_until_complete(http_exception_handler(req, exc))
    finally:
        loop.close()

    assert resp.status_code == 418
    # resp.body is bytes
    data = json.loads(resp.body)
    assert data == {"error": "I'm a teapot"}

def test_validation_exception_handler():
    # Simulate a Pydantic request validation error
    scope = {"type": "http", "method": "POST", "path": "/add", "headers": []}
    req = Request(scope)
    errors = [{"loc": ["body", "a"], "msg": "bad input", "type": "value_error"}]
    exc = RequestValidationError(errors)

    loop = asyncio.new_event_loop()
    try:
        resp: JSONResponse = loop.run_until_complete(validation_exception_handler(req, exc))
    finally:
        loop.close()

    assert resp.status_code == 400
    data = json.loads(resp.body)
    assert data == {"error": "a: bad input"}
