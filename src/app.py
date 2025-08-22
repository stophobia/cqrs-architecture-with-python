from fastapi import FastAPI
from fastapi_pagination import add_pagination

from containers import OrderContainer
from rest import init_middlewares, init_routes
from settings import APPLICATION_NAME


def create_app() -> FastAPI:
    container = OrderContainer()
    container.init_resources()
    container.wire(modules=[__name__])

    # Creation of the FastAPI application instance
    app = FastAPI(
        title=APPLICATION_NAME,
        description='FastAPI application using cqrs architecture',
    )

    # Initialization of middlewares and routes
    init_middlewares(app)
    init_routes(
        app,
        [
            container.order_controller(),
        ],
    )

    # Addition of pagination support
    add_pagination(app)

    return app
