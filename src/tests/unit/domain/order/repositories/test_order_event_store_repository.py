# pylint: disable=redefined-outer-name
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from pymongo.errors import DuplicateKeyError

from domain.base.event import DomainEvent
from domain.order.exceptions.order_exceptions import EntityOutdated, PersistenceError
from domain.order.model.entities import Order
from domain.order.repositories.order_event_store_repository import OrderEventStoreRepository


def make_event(order: Order, **kwargs) -> DomainEvent:
    return DomainEvent(
        event_name=kwargs.get('event_name', 'OrderCreated'),
        aggregate=order,
        version=kwargs.get('version', 0),
        tracker_id=kwargs.get('tracker_id', uuid4()),
    )


@pytest_asyncio.fixture
def order_event_store_repository():
    collection = MagicMock()

    cursor = MagicMock()
    cursor.to_list = AsyncMock()
    collection.find.return_value = cursor
    collection.insert_one = AsyncMock()

    connection_cm = AsyncMock()
    connection_cm.__aenter__.return_value = {'events': collection}
    connection_cm.__aexit__.return_value = None

    db_connection = MagicMock()
    db_connection.get_connection.return_value = connection_cm

    repository = OrderEventStoreRepository(
        db_connection=db_connection,
        collection_name='events',
    )
    return repository


@pytest.mark.asyncio
async def test_from_id_returns_events(order_event_store_repository):
    repo = order_event_store_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    cursor = collection.find.return_value
    order = Order(buyer_id='b1', items=[], product_cost=10, delivery_cost=5, payment_id='p1')
    event = make_event(order)
    cursor.to_list.return_value = [event.model_dump(mode='json')]
    result = await repo.from_id(order.id)
    assert isinstance(result[0], DomainEvent)


@pytest.mark.asyncio
async def test_from_id_returns_none(order_event_store_repository):
    repo = order_event_store_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    cursor = collection.find.return_value
    cursor.to_list.return_value = []
    result = await repo.from_id('missing')
    assert result is None


@pytest.mark.asyncio
async def test_save_inserts_new_event(order_event_store_repository):
    repo = order_event_store_repository
    repo.get_last_event_version_from_entity = AsyncMock(return_value=None)
    order = Order(buyer_id='b2', items=[], product_cost=20, delivery_cost=10, payment_id='p2')
    event = make_event(order)
    await repo.save(event)
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    collection.insert_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_updates_event_version(order_event_store_repository):
    repo = order_event_store_repository
    last_order = Order(buyer_id='b3', items=[], product_cost=30, delivery_cost=15, payment_id='p3')
    last_event = make_event(last_order, version=1)
    repo.get_last_event_version_from_entity = AsyncMock(return_value=last_event)
    order = Order(buyer_id='b3', items=[], product_cost=30, delivery_cost=15, payment_id='p3')
    event = make_event(order)
    await repo.save(event)
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    args, _ = collection.insert_one.call_args
    assert args[0]['version'] == 2


@pytest.mark.asyncio
async def test_save_raises_entity_outdated(order_event_store_repository):
    repo = order_event_store_repository
    old_order = Order(buyer_id='b4', items=[], product_cost=40, delivery_cost=20, payment_id='p4')
    old_order.version = 5
    last_event = make_event(old_order, version=5)
    repo.get_last_event_version_from_entity = AsyncMock(return_value=last_event)
    new_order = Order(buyer_id='b4', items=[], product_cost=40, delivery_cost=20, payment_id='p4')
    new_order.version = 1
    event = make_event(new_order)
    with pytest.raises(EntityOutdated):
        await repo.save(event)


@pytest.mark.asyncio
async def test_save_raises_persistence_error_on_duplicate(order_event_store_repository):
    repo = order_event_store_repository
    repo.get_last_event_version_from_entity = AsyncMock(return_value=None)
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    collection.insert_one.side_effect = DuplicateKeyError('dup')
    order = Order(buyer_id='b5', items=[], product_cost=50, delivery_cost=25, payment_id='p5')
    event = make_event(order)
    with pytest.raises(PersistenceError):
        await repo.save(event)


@pytest.mark.asyncio
async def test_get_all_events_by_tracker_id_returns_events(order_event_store_repository):
    repo = order_event_store_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    cursor = collection.find.return_value
    order = Order(buyer_id='b6', items=[], product_cost=60, delivery_cost=30, payment_id='p6')
    event = make_event(order)
    cursor.to_list.return_value = [event.model_dump(mode='json')]
    result = await repo.get_all_events_by_tracker_id(str(event.tracker_id))
    assert isinstance(result[0], DomainEvent)


@pytest.mark.asyncio
async def test_get_all_events_by_tracker_id_returns_empty(order_event_store_repository):
    repo = order_event_store_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    cursor = collection.find.return_value
    cursor.to_list.return_value = []
    result = await repo.get_all_events_by_tracker_id('missing')
    assert result == []


@pytest.mark.asyncio
async def test_get_last_event_version_from_entity_returns_event(order_event_store_repository):
    repo = order_event_store_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    cursor = collection.find.return_value
    order = Order(buyer_id='b7', items=[], product_cost=70, delivery_cost=35, payment_id='p7')
    event = make_event(order, version=3)
    doc = event.model_dump(mode='json')
    doc['_id'] = 'ignore'
    cursor.to_list.return_value = [doc]
    result = await repo.get_last_event_version_from_entity(order.id)
    assert isinstance(result, DomainEvent)
    assert result.version == 3


@pytest.mark.asyncio
async def test_get_last_event_version_from_entity_returns_none(order_event_store_repository):
    repo = order_event_store_repository
    collection = repo.db_connection.get_connection.return_value.__aenter__.return_value['events']
    cursor = collection.find.return_value
    cursor.to_list.return_value = []
    result = await repo.get_last_event_version_from_entity('missing')
    assert result is None


@pytest.mark.asyncio
async def test_rebuild_aggregate_root_success(order_event_store_repository):
    repo = order_event_store_repository
    order = Order(buyer_id='b8', items=[], product_cost=80, delivery_cost=40, payment_id='p8')
    event = make_event(order)
    result = await repo.rebuild_aggregate_root(event, Order)
    assert isinstance(result, Order)


@pytest.mark.asyncio
async def test_rebuild_aggregate_root_raises_persistence_error(order_event_store_repository):
    repo = order_event_store_repository

    class FakeAgg:
        def model_dump(self):
            return {'invalid': 'x'}

    bad_event = DomainEvent(event_name='BadEvent', aggregate=FakeAgg(), tracker_id=uuid4())
    with pytest.raises(PersistenceError):
        await repo.rebuild_aggregate_root(bad_event, Order)
