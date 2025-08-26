import abc
from typing import Annotated

from domain.delivery.ports.cost_calculator_interface import (  # noqa: E501
    DeliveryCostCalculatorAdapterInterface,
)
from domain.maps.model.value_objects import Address
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.ports.order_event_store_repository_interface import (
    OrderEventStoreRepositoryInterface,
)
from domain.order.ports.order_repository_interface import (
    OrderRepositoryInterface,
)
from domain.payment.ports.payment_adapter_interface import (  # noqa: E501
    PaymentAdapterInterface,
)
from domain.product.ports.product_adapter_interface import (  # noqa: E501
    ProductAdapterInterface,
)


class OrderServiceInterface(abc.ABC):
    """Interface for command orders."""

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        repository: OrderRepositoryInterface,
        payment_service: PaymentAdapterInterface,
        product_service: ProductAdapterInterface,
        delivery_service: DeliveryCostCalculatorAdapterInterface,
        event_store: OrderEventStoreRepositoryInterface,
    ) -> None:
        """Initialize dependencies for the order service."""
        self.repository = repository
        self.payment_service = payment_service
        self.product_service = product_service
        self.delivery_service = delivery_service
        self.event_store = event_store

    @abc.abstractmethod
    async def create_new_order(
        self,
        buyer_id: Annotated[str, BuyerId],
        items: list[OrderItem],
        destination: Address,
    ) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def pay_order(self, order_id: Annotated[str, OrderId]) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def cancel_order(self, order_id: Annotated[str, OrderId]) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def _pay_order_tnx(
        self, order_id: Annotated[str, OrderId], is_payment_verified: bool
    ) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_order_from_id(self, order_id: Annotated[str, OrderId]) -> Order:
        raise NotImplementedError()
