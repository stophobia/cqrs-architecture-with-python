import uuid
from collections.abc import Sequence
from decimal import Decimal

from bson import ObjectId
from pydantic import ConfigDict, Field, computed_field

from domain.base.dto import DataTransferObject
from domain.order.model.entities import Order
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem, OrderStatusEnum
from domain.payment.model.value_objects import PaymentId


class Address(DataTransferObject):
    """Postal address DTO."""

    house_number: str | int | None
    road: str
    sub_district: str
    district: str
    state: str
    postcode: str
    country: str

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'house_number': '70',
                'road': 'Rua Padre Emilio Hartmann',
                'sub_district': 'Hípica',
                'district': 'Porto Alegre',
                'state': 'RS',
                'postcode': '91755720',
                'country': 'Brazil',
            }
        }
    )


class OrderCreateRequest(DataTransferObject):
    """Create-order request payload."""

    buyer_id: BuyerId
    items: Sequence[OrderItem]
    destination: Address

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            'example': {
                'buyer_id': str(ObjectId()),
                'items': [{'product_id': uuid.uuid4().hex, 'amount': 200}],
                'destination': Address.model_json_schema()['example'],
            }
        },
    )


class OrderCreateResponse(DataTransferObject):
    """Create-order response payload."""

    order_id: OrderId

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
            }
        }
    )


class OrderUpdateStatusRequest(DataTransferObject):
    """Update-order-status request payload."""

    status: OrderStatusEnum

    model_config = ConfigDict(json_schema_extra={'example': {'status': OrderStatusEnum.CANCELLED}})


class OrderUpdateStatusResponse(DataTransferObject):
    """Update-order-status response payload."""

    order_id: OrderId
    status: OrderStatusEnum

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
                'status': OrderStatusEnum.PAID,
            }
        }
    )

    @classmethod
    def from_order_id(cls, order_id: OrderId) -> 'OrderUpdateStatusResponse':
        """Factory from identifier."""
        return cls(order_id=order_id)


class OrderDetail(DataTransferObject):
    """Order detail view."""

    order_id: OrderId = Field(validation_alias='id')
    buyer_id: BuyerId
    payment_id: PaymentId
    items: Sequence[OrderItem]
    product_cost: Decimal
    delivery_cost: Decimal
    status: OrderStatusEnum

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'order_id': str(ObjectId()),
                'buyer_id': str(ObjectId()),
                'payment_id': uuid.uuid4().hex,
                'items': [{'product_id': uuid.uuid4().hex, 'amount': 200}],
                'product_cost': '424.20',
                'delivery_cost': '42.42',
                'total_cost': '466.62',
                'status': OrderStatusEnum.WAITING,
            }
        }
    )

    @computed_field  # type: ignore[misc]
    @property
    def total_cost(self) -> Decimal:
        """Computed total (products + delivery)."""
        return self.product_cost + self.delivery_cost

    @classmethod
    def from_order(cls, order: Order) -> 'OrderDetail':
        """Factory from aggregate."""
        return cls.model_validate(order.model_dump())
