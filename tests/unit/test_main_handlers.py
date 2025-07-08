
import pytest
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.requests import Request
from fastapi.responses import JSONResponse
from main import (
    OperationRequest,
    http_exception_handler,
    validation_exception_handler,
)

def test_validate_numbers_direct():
    # call the field_validator directly
    with pytest.raises(ValueError) as exc:
        OperationRequest.validate_numbers(OperationRequest, "not a number")
    assert "Both a and b must be numbers." in str(exc.value)

@pytest.mark.asyncio
async def test_http_exception_handler():
    scope = {"type": "http", "method": "GET", "path": "/foo", "headers": []}
    request = Request(scope)
    exc = HTTPException(status_code=418, detail="I'm a teapot")
    resp = await http_exception_handler(request, exc)
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 418
    assert resp.json() == {"error": "I'm a teapot"}

@pytest.mark.asyncio
async def test_validation_exception_handler():
    scope = {"type": "http", "method": "POST", "path": "/add", "headers": []}
    request = Request(scope)
    errors = [{"loc": ["body", "a"], "msg": "bad input", "type": "value_error"}]
    exc = RequestValidationError(errors)
    resp = await validation_exception_handler(request, exc)
    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 400
    assert resp.json() == {"error": "a: bad input"}
