
import pytest
import json
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
    # directly exercise the raw validator (it should reject non-numeric)
    with pytest.raises(ValueError) as exc:
        OperationRequest.validate_numbers("foo")
    assert str(exc.value) == "Both a and b must be numbers."

@pytest.mark.anyio
async def test_http_exception_handler():
    # simulate an HTTPException handler
    scope = {"type": "http", "method": "GET", "path": "/foo", "headers": []}
    req = Request(scope)
    exc = HTTPException(status_code=418, detail="I'm a teapot")
    resp: JSONResponse = await http_exception_handler(req, exc)
    assert resp.status_code == 418
    data = json.loads(resp.body)
    assert data == {"error": "I'm a teapot"}

@pytest.mark.anyio
async def test_validation_exception_handler():
    # simulate a Pydantic validation error handler
    scope = {"type": "http", "method": "POST", "path": "/add", "headers": []}
    req = Request(scope)
    errors = [{"loc": ["body", "a"], "msg": "bad input", "type": "value_error"}]
    exc = RequestValidationError(errors)
    resp: JSONResponse = await validation_exception_handler(req, exc)
    assert resp.status_code == 400
    data = json.loads(resp.body)
    assert data == {"error": "a: bad input"}
