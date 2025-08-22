from __future__ import annotations

from typing import Annotated

from domain.order.exceptions.order_exceptions import EntityOutdated, PersistenceError
from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from domain.order.ports.order_repository_interface import OrderRepositoryInterface


class OrderRepository(OrderRepositoryInterface):
    """Repository for storing and retrieving order aggregates."""

    def _key(self, order_id: OrderId | str) -> str:
        """Normalize the aggregate identifier."""
        return str(order_id)

    async def from_id(self, order_id: OrderId) -> Order | None:
        """Load an order aggregate by id."""
        key = self._key(order_id)
        if order_result := await self.cache_adapter.get(key=key):
            return Order.model_validate(order_result)

        async with self.db_connection.get_connection() as connection:
            document = await connection[self.collection_name].find_one({'_id': key})
            if not document:
                return None
            order = Order.model_validate(document)
            await self.cache_adapter.set(key=key, data=order.model_dump(mode='json'))
            return order

    async def save(self, order: Order) -> None:
        """Persist an order aggregate with optimistic concurrency."""
        key = self._key(order.id)
        current = await self.from_id(order.id)
        if current and order.version < current.version:
            raise EntityOutdated(detail='incoming aggregate version is outdated')

        if current:
            order.version = current.version

        order.increase_version()

        async with self.db_connection.get_connection() as connection:
            try:
                await connection[self.collection_name].replace_one(
                    {'_id': key},
                    order.model_dump(mode='json'),
                    upsert=True,
                )
            except Exception as exc:
                raise PersistenceError(detail='failed to persist order') from exc

        await self.cache_adapter.set(key=key, data=order.model_dump(mode='json'))

    async def delete(self, order_id: Annotated[str, OrderId]) -> None:
        """Delete an order aggregate by id."""
        key = self._key(order_id)
        await self.cache_adapter.delete(key=key)
        async with self.db_connection.get_connection() as connection:
            await connection[self.collection_name].delete_one({'_id': key})
