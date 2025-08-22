import abc
from typing import Annotated

from adapters.mongo_db_connector_adapter import AsyncMongoDBConnectorAdapter
from domain.order.model.entities import Order
from domain.order.model.value_objects import OrderId
from ports.cache_interface import CacheInterface


class OrderRepositoryInterface(abc.ABC):
    """Interface for managing order aggregates."""

    def __init__(
        self,
        cache_adapter: CacheInterface,
        db_connection: AsyncMongoDBConnectorAdapter,
        collection_name: str,
    ):
        self.cache_adapter = cache_adapter
        self.db_connection = db_connection
        self.collection_name = collection_name

    @abc.abstractmethod
    async def from_id(self, order_id: Annotated[str, OrderId]) -> Order | None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def save(self, order: Order) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, order_id: Annotated[str, OrderId]) -> None:
        raise NotImplementedError()
