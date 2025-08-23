from enum import Enum

from domain.base.event import DomainEvent


class OrderEventName(str, Enum):
    """Enumeration of domain events related to order lifecycle."""

    CREATED = 'payment_order_created'
    CANCELLED = 'payment_order_cancelled'
    PAID = 'payment_order_paid'

    def __str__(self) -> str:
        return self.value


class OrderCreated(DomainEvent):
    """Event emitted when an order is created."""

    event_name: str = OrderEventName.CREATED.value


class OrderPaid(DomainEvent):
    """Event emitted when an order is paid."""

    event_name: str = OrderEventName.PAID.value


class OrderCancelled(DomainEvent):
    """Event emitted when an order is cancelled."""

    event_name: str = OrderEventName.CANCELLED.value
