from unittest.mock import MagicMock

import pytest

from adapters.event_publisher_adapter import DummyEventPublisher


class FakeDomainEvent:
    def model_dump(self, mode='json'):
        return {'fake': True, 'mode': mode}


@pytest.mark.asyncio
async def test_publish_accepts_domain_event(monkeypatch):
    event = MagicMock()
    event.model_dump.return_value = {'id': 1}

    publisher = DummyEventPublisher()
    await publisher.publish(event)

    event.model_dump.assert_called_once_with(mode='json')
