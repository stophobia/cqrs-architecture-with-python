from unittest.mock import MagicMock

import pytest

from adapters.event_publisher_adapter import DummyEventPublisher


class FakeDomainEvent:
    def model_dump_json(self, indent=None):
        return f"{{'fake': true, 'indent': {indent}}}"


@pytest.mark.asyncio
async def test_publish_prints_event(capfd):
    event = FakeDomainEvent()
    publisher = DummyEventPublisher()

    await publisher.publish(event)

    captured = capfd.readouterr()
    assert "{'fake': true" in captured.out
    assert 'indent' in captured.out


@pytest.mark.asyncio
async def test_publish_accepts_domain_event(monkeypatch):
    event = MagicMock()
    event.model_dump_json.return_value = '{"id": 1}'

    publisher = DummyEventPublisher()
    await publisher.publish(event)

    event.model_dump_json.assert_called_once_with(indent=2)
