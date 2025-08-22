# pylint: disable=redefined-outer-name, protected-access, unnecessary-dunder-call
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from adapters.mongo_db_connector_adapter import (
    AsyncMongoDBConnectorAdapter,
    MongoDBAdapterException,
)


@pytest.fixture
def connection_str():
    return 'mongodb://localhost:27017'


@pytest.fixture
def database_name():
    return 'test_db'


@pytest.fixture
def fake_client(database_name):
    mock_client = MagicMock(spec=AsyncIOMotorClient)
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    return mock_client


@pytest.mark.asyncio
async def test_get_connection_success(connection_str, database_name, fake_client):
    adapter = AsyncMongoDBConnectorAdapter(connection_str, database_name, client=fake_client)
    async with adapter.get_connection() as conn:
        assert conn is fake_client[database_name]


@pytest.mark.asyncio
@pytest.mark.parametrize('error', [ServerSelectionTimeoutError(), ConnectionFailure()])
async def test_get_connection_raises_and_resets(error, connection_str, database_name):
    with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__getitem__.side_effect = error
        mock_client.close = AsyncMock()
        mock_client_cls.return_value = mock_client

        adapter = AsyncMongoDBConnectorAdapter(connection_str, database_name)

        with pytest.raises(MongoDBAdapterException) as exc_info:
            async with adapter.get_connection():
                pass

        assert 'has been reset' in str(exc_info.value)
        mock_client.close.assert_awaited_once()
        assert adapter._client is None
        assert adapter._database is None


@pytest.mark.asyncio
async def test_close_and_reset_connection(connection_str, database_name, fake_client):
    fake_client.close = AsyncMock()
    adapter = AsyncMongoDBConnectorAdapter(connection_str, database_name, client=fake_client)

    await adapter.close()

    fake_client.close.assert_awaited_once()
    assert adapter._client is None
    assert adapter._database is None


def test_ensure_connection_creates_client(connection_str, database_name):
    adapter = AsyncMongoDBConnectorAdapter(connection_str, database_name)

    with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_client.__getitem__.return_value = MagicMock()
        mock_client_cls.return_value = mock_client

        adapter._ensure_connection()
        mock_client_cls.assert_called_once()
        assert adapter._client is not None
        assert adapter._database is not None


def test_del_with_event_loop_running(connection_str, database_name):
    fake_client = MagicMock()
    fake_client.close = AsyncMock()
    adapter = AsyncMongoDBConnectorAdapter(connection_str, database_name, client=fake_client)

    loop = asyncio.get_event_loop()
    with (
        patch.object(loop, 'is_running', return_value=True),
        patch.object(loop, 'create_task') as mock_task,
    ):
        adapter.__del__()
        mock_task.assert_called_once()


def test_del_event_loop_not_running(connection_str, database_name):
    fake_client = MagicMock()
    adapter = AsyncMongoDBConnectorAdapter(connection_str, database_name, client=fake_client)

    with patch('asyncio.get_event_loop', side_effect=RuntimeError):
        adapter.__del__()


@pytest.mark.asyncio
async def test_reuses_same_connection_instance(connection_str, database_name):
    with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_database = MagicMock()
        mock_client.__getitem__.return_value = mock_database
        mock_client_cls.return_value = mock_client

        adapter = AsyncMongoDBConnectorAdapter(connection_str, database_name)

        async with adapter.get_connection() as db1:
            pass
        async with adapter.get_connection() as db2:
            pass

        mock_client_cls.assert_called_once_with(
            connection_str,
            serverSelectionTimeoutMS=15000,
            uuidRepresentation='standard',
        )
        mock_client.__getitem__.assert_called_once_with(database_name)
        assert db1 is db2
