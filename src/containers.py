from dependency_injector import containers, providers

import settings
from adapters.event_publisher_adapter import DummyEventPublisher
from adapters.mongo_db_connector_adapter import AsyncMongoDBConnectorAdapter
from adapters.redis_adapter import RedisAdapter
from domain.delivery.adapters.cost_calculator_adapter import (
    DeliveryCostCalculatorAdapter,
)
from domain.maps.adapters.google_maps_adapter import GoogleMapsAdapter
from domain.order.controllers.order_controller import OrderController
from domain.order.repositories.order_event_store_repository import (
    OrderEventStoreRepository,
)
from domain.order.repositories.order_repository import (
    OrderRepository,
)
from domain.order.services.order_service import OrderService
from domain.payment.adapters.paypal_adapter import PayPalPaymentAdapter
from domain.product.adapters.product_adapter import ProductAdapter


class OrderContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[__name__])
    config = providers.Configuration()

    cache_adapter = providers.Singleton(RedisAdapter, silent_mode=settings.CACHE_SILENT_MODE)
    event_publisher = providers.Singleton(DummyEventPublisher)
    maps_adapter = providers.Singleton(GoogleMapsAdapter)

    order_event_store_connection = providers.Singleton(
        AsyncMongoDBConnectorAdapter,
        connection_str=settings.ORDER_EVENT_STORE_CONNECTION,
        database_name=settings.ORDER_EVENT_STORE_DATABASE_NAME,
    )

    order_repository_connection = providers.Singleton(
        AsyncMongoDBConnectorAdapter,
        connection_str=settings.ORDER_REPOSITORY_CONNECTION,
        database_name=settings.ORDER_REPOSITORY_DATABASE_NAME,
    )

    order_event_store_repository = providers.Factory(
        OrderEventStoreRepository,
        db_connection=order_event_store_connection,
        collection_name=settings.ORDER_EVENT_STORE_COLLECTION_NAME,
    )

    order_repository = providers.Factory(
        OrderRepository,
        cache_adapter=cache_adapter,
        db_connection=order_repository_connection,
        collection_name=settings.ORDER_REPOSITORY_COLLECTION_NAME,
    )

    # Services
    delivery_cost_calculator = providers.Singleton(
        DeliveryCostCalculatorAdapter, maps_service=maps_adapter
    )

    order_service = providers.Factory(
        OrderService,
        repository=order_repository,
        payment_service=providers.Singleton(PayPalPaymentAdapter),
        product_service=providers.Singleton(ProductAdapter),
        delivery_service=delivery_cost_calculator,
        event_publisher=event_publisher,
    )

    # Controller
    order_controller = providers.Factory(OrderController, order_service=order_service)
