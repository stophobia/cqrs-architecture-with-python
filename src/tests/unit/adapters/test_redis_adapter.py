# pylint: disable=unnecessary-dunder-call, protected-access
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from adapters.redis_adapter import RedisAdapter


@pytest.mark.asyncio
async def test_set_and_get():
    mock_client = AsyncMock()
    mock_client.get.return_value = json.dumps({'foo': 'bar'})
    adapter = RedisAdapter()
    adapter.client = mock_client

    await adapter.set('key', {'foo': 'bar'})
    result = await adapter.get('key')

    mock_client.set.assert_awaited_once()
    mock_client.get.assert_awaited_once_with('key')
    assert result == {'foo': 'bar'}


@pytest.mark.asyncio
async def test_get_returns_none():
    mock_client = AsyncMock()
    mock_client.get.return_value = None
    adapter = RedisAdapter()
    adapter.client = mock_client

    result = await adapter.get('missing')
    assert result is None


@pytest.mark.asyncio
async def test_delete():
    mock_client = AsyncMock()
    adapter = RedisAdapter()
    adapter.client = mock_client

    await adapter.delete('key')
    mock_client.delete.assert_awaited_once_with('key')


@pytest.mark.asyncio
async def test_silent_mode_returns_false_on_exception(caplog):
    mock_client = AsyncMock()
    mock_client.get.side_effect = RuntimeError('boom')
    adapter = RedisAdapter(silent_mode=True)
    adapter.client = mock_client

    result = await adapter.get('key')
    assert result is False
    assert 'Cache silent exception' in caplog.text


@pytest.mark.asyncio
async def test_silent_mode_disabled_propagates_exception():
    mock_client = AsyncMock()
    mock_client.get.side_effect = RuntimeError('boom')
    adapter = RedisAdapter(silent_mode=False)
    adapter.client = mock_client

    with pytest.raises(RuntimeError):
        await adapter.get('key')


def test_open_connection_builds_correct_url(monkeypatch):
    monkeypatch.setattr('adapters.redis_adapter.REDIS_HOST', 'localhost')
    monkeypatch.setattr('adapters.redis_adapter.REDIS_PORT', 6379)
    monkeypatch.setattr('adapters.redis_adapter.REDIS_PASSWORD', 'secret')
    monkeypatch.setattr('adapters.redis_adapter.REDIS_SSL', True)

    mock_from_url = MagicMock()
    monkeypatch.setattr('adapters.redis_adapter.aioredis.from_url', mock_from_url)

    RedisAdapter._RedisAdapter__open_connection()
    mock_from_url.assert_called_once()
    called_url = mock_from_url.call_args[0][0]
    assert called_url.startswith('rediss://:secret@localhost:6379')


def test_del_with_running_loop(monkeypatch):
    mock_loop = MagicMock()
    mock_loop.is_running.return_value = True
    monkeypatch.setattr('asyncio.get_event_loop', lambda: mock_loop)

    adapter = RedisAdapter()
    adapter.client = AsyncMock()

    adapter.__del__()
    mock_loop.create_task.assert_called()


def test_del_with_not_running_loop(monkeypatch):
    mock_loop = MagicMock()
    mock_loop.is_running.return_value = False
    monkeypatch.setattr('asyncio.get_event_loop', lambda: mock_loop)

    adapter = RedisAdapter()
    adapter.client = AsyncMock()

    adapter.__del__()
    mock_loop.run_until_complete.assert_called()
