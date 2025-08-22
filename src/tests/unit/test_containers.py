from adapters.event_publisher_adapter import DummyEventPublisher
from adapters.mongo_db_connector_adapter import AsyncMongoDBConnectorAdapter
from adapters.redis_adapter import RedisAdapter
from domain.delivery.adapters.cost_calculator_adapter import DeliveryCostCalculatorAdapter
from domain.maps.adapters.google_maps_adapter import GoogleMapsAdapter
from domain.order.controllers.order_controller import OrderController
from domain.order.repositories.order_event_store_repository import OrderEventStoreRepository
from domain.order.repositories.order_repository import OrderRepository
from domain.order.services.order_service import OrderService
from domain.payment.adapters.paypal_adapter import PayPalPaymentAdapter
from domain.product.adapters.product_adapter import ProductAdapter
from src.containers import OrderContainer


def test_container_initialization():
    container = OrderContainer()
    service = container.order_service()
    assert service is not None


def test_cache_adapter_provider():
    container = OrderContainer()
    cache = container.cache_adapter()
    assert isinstance(cache, RedisAdapter)


def test_event_publisher_provider():
    container = OrderContainer()
    publisher = container.event_publisher()
    assert isinstance(publisher, DummyEventPublisher)


def test_maps_adapter_provider():
    container = OrderContainer()
    maps = container.maps_adapter()
    assert isinstance(maps, GoogleMapsAdapter)


def test_order_event_store_connection_provider():
    container = OrderContainer()
    conn = container.order_event_store_connection()
    assert isinstance(conn, AsyncMongoDBConnectorAdapter)


def test_order_repository_connection_provider():
    container = OrderContainer()
    conn = container.order_repository_connection()
    assert isinstance(conn, AsyncMongoDBConnectorAdapter)


def test_order_event_store_repository_provider():
    container = OrderContainer()
    repo = container.order_event_store_repository()
    assert isinstance(repo, OrderEventStoreRepository)


def test_order_repository_provider():
    container = OrderContainer()
    repo = container.order_repository()
    assert isinstance(repo, OrderRepository)


def test_delivery_cost_calculator_provider():
    container = OrderContainer()
    svc = container.delivery_cost_calculator()
    assert isinstance(svc, DeliveryCostCalculatorAdapter)


def test_order_service_provider():
    container = OrderContainer()
    service = container.order_service()
    assert isinstance(service, OrderService)
    assert isinstance(service.repository, OrderRepository)
    assert isinstance(service.payment_service, PayPalPaymentAdapter)
    assert isinstance(service.product_service, ProductAdapter)
    assert isinstance(service.delivery_service, DeliveryCostCalculatorAdapter)
    assert isinstance(service.event_publisher, DummyEventPublisher)


def test_order_controller_provider():
    container = OrderContainer()
    controller = container.order_controller()
    assert isinstance(controller, OrderController)
    assert isinstance(controller.order_service, OrderService)
