from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from decouple import config
from fastapi import HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.utils import is_body_allowed_for_status_code

APPLICATION_NAME: str = config('APPLICATION_NAME', default='ordering-service', cast=str)


class OrderingServiceException(HTTPException):
    """Base exception for the Ordering Service with structured error information."""

    message: str = 'Internal Server Error'
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    name: str = 'INTERNAL_ERROR'
    service: str = APPLICATION_NAME

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        message: str | None = None,
        status_code: int | None = None,
        detail: Any | None = None,
        name: str | None = None,
        service: str | None = None,
        headers: dict[str, str] | None = None,
        errors: Sequence[Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.service = service or self.service
        self.name = name or self.name
        self.status_code = status_code or self.status_code
        self.headers = headers
        self._errors: tuple[Any, ...] = tuple(errors) if errors else ()
        self.detail = detail or self.message
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)

    def errors(self) -> Sequence[Any]:
        """Return structured error details, if any."""
        return self._errors


async def http_exception_handler(request: Request, exc: OrderingServiceException) -> Response:
    """Custom HTTP exception handler that returns a structured JSON response."""
    headers = getattr(exc, 'headers', None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)

    response_data = {
        'service': exc.service,
        'detail': exc.detail,
        'name': exc.name,
        'errors': jsonable_encoder(exc.errors()),
        'resource': request.url.path,
    }

    return JSONResponse(content=response_data, status_code=exc.status_code, headers=headers)
