from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core import constants

class ExceptionHandlers:
    async def http_exception_handler(self, request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": False, "message": exc.detail, "data": None},
        )

    async def validation_exception_handler(self, request: Request, exc: RequestValidationError):
        errors = exc.errors()
        first_error_msg = errors[0]["msg"] if errors else "Validation error"
        return JSONResponse(
            status_code=422,
            content={
                "status": False,
                "message": first_error_msg,
                "data": errors,
            },
        )