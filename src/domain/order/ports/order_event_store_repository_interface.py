import abc

from adapters.mongo_db_connector_adapter import AsyncMongoDBConnectorAdapter
from domain.base.event import DomainEvent
from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId


class OrderEventStoreRepositoryInterface(abc.ABC):
    """Port for the Order aggregate event store."""

    def __init__(
        self,
        db_connection: AsyncMongoDBConnectorAdapter,
        collection_name: str,
    ):
        self.db_connection = db_connection
        self.collection_name = collection_name

    @abc.abstractmethod
    async def from_id(self, order_id: OrderId) -> list[DomainEvent] | None:
        """Return all domain events for a given aggregate id, or None if none found."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def save(self, event: DomainEvent) -> None:
        """Persist a domain event with optimistic concurrency guarantees."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_all_events_by_tracker_id(self, tracker_id: str) -> list[DomainEvent]:
        """Return all events correlated by a tracker id."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_last_event_version_from_entity(self, order_id: OrderId) -> DomainEvent | None:
        """Return the most recent event for a given aggregate id, or None if not found."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def rebuild_aggregate_root(
        self, event: DomainEvent, aggregate_class: type[Order]
    ) -> Order:
        """Rehydrate an aggregate root from a domain event payload."""
        raise NotImplementedError()
