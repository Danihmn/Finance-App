from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from services.exceptions import (
    AlreadyExistsError,
    InvalidDataError,
    NotFoundError,
    ServiceError,
    ServiceUnavailableError,
)

_STATUS: dict[type[ServiceError], tuple[int, str]] = {
    AlreadyExistsError: (status.HTTP_409_CONFLICT, "Record already exists"),
    InvalidDataError: (status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid data"),
    NotFoundError: (status.HTTP_404_NOT_FOUND, "Record not found"),
    ServiceUnavailableError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Service unavailable",
    ),
    ServiceError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error"),
}


def register_exception_handlers(app: FastAPI) -> None:
    for error_class, (status_code, detail) in _STATUS.items():

        def handler(
            request: Request, exc: Exception, status_code=status_code, detail=detail
        ) -> JSONResponse:
            return JSONResponse(status_code=status_code, content={"detail": detail})

        app.add_exception_handler(error_class, handler)
