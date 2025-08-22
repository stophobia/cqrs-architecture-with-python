from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from exceptions import OrderingServiceException, http_exception_handler


def init_middlewares(app: FastAPI) -> None:
    """Initialize application middlewares."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def init_routes(app: FastAPI, controllers: list[object]) -> None:
    """Register application routes and exception handlers."""

    @app.get('/', status_code=status.HTTP_200_OK, include_in_schema=False)
    async def health_check() -> dict[str, int]:
        return {'status': status.HTTP_200_OK}

    for controller in controllers:
        app.include_router(controller.router)

    @app.exception_handler(OrderingServiceException)
    @app.exception_handler(Exception)
    async def service_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        exception = exc if isinstance(exc, OrderingServiceException) else OrderingServiceException()
        return await http_exception_handler(request, exception)

    @app.exception_handler(NotImplementedError)
    async def not_implemented_error_handler(
        request: Request, exc: NotImplementedError
    ) -> JSONResponse:
        return JSONResponse(
            content={'error': 'Method Not Allowed.'},
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
