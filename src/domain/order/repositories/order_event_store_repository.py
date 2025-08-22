from __future__ import annotations

from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from domain.base.event import DomainEvent
from domain.order.exceptions.order_exceptions import EntityOutdated, PersistenceError
from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.order_event_store_repository_interface import (
    OrderEventStoreRepositoryInterface,
)


class OrderEventStoreRepository(OrderEventStoreRepositoryInterface):
    """Repository for storing and retrieving order domain events using event sourcing."""

    async def from_id(self, order_id: OrderId) -> list[DomainEvent] | None:
        """Load all domain events for a given aggregate id."""
        connection = await self.db_connection.get_connection()
        cursor = connection[self.collection_name].find({'aggregate.order_id': str(order_id)})
        events_list = await cursor.to_list(length=None)
        if not events_list:
            return None
        return [DomainEvent.parse_obj(event) for event in events_list]

    async def save(self, event: DomainEvent) -> None:
        """Persist a new domain event with optimistic concurrency checks."""
        aggregate_root = event.aggregate
        last_event = await self.get_last_event_version_from_entity(aggregate_root.order_id)

        if last_event:
            aggregate_root_old = Order.model_validate(last_event.aggregate)
            if aggregate_root_old and aggregate_root_old.version > aggregate_root.version:
                raise EntityOutdated(
                    detail=f"incoming version {aggregate_root.version} "
                    f"is behind current {aggregate_root_old.version}"
                )
            event.version = last_event.version
            event.increase_version()
            event.tracker_id = last_event.tracker_id
        else:
            event.increase_version()

        connection = await self.db_connection.get_connection()
        try:
            await connection[self.collection_name].insert_one(event.to_dict())
        except DuplicateKeyError as exc:
            raise PersistenceError(detail=f"duplicate event id {event.id}") from exc

    async def get_all_events_by_tracker_id(self, tracker_id: str) -> list[DomainEvent]:
        """Retrieve all events correlated by a tracker id."""
        connection = await self.db_connection.get_connection()
        cursor = connection[self.collection_name].find({'tracker_id': tracker_id})
        events_list = await cursor.to_list(length=None)
        return [DomainEvent.parse_obj(event) for event in events_list] if events_list else []

    async def get_last_event_version_from_entity(self, order_id: OrderId) -> DomainEvent | None:
        """Return the most recent event for a given aggregate id."""
        connection = await self.db_connection.get_connection()
        cursor = connection[self.collection_name].find(
            {'aggregate.order_id': str(order_id)},
            sort=[('version', -1)],
            limit=1,
        )
        events_list = await cursor.to_list(length=None)
        if not events_list:
            return None
        event = events_list[0]
        event.pop('_id', None)
        return DomainEvent.parse_obj(event)

    async def rebuild_aggregate_root(
        self, event: DomainEvent, aggregate_class: type[Order]
    ) -> Order:
        """Rehydrate an aggregate from a domain event."""
        try:
            return aggregate_class.parse_obj(event.aggregate.dict())
        except ValidationError as exc:
            raise PersistenceError(detail='invalid aggregate reconstruction') from exc
