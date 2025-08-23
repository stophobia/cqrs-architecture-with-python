from domain.base.event import DomainEvent
from domain.base.ports.event_adapter_interface import DomainEventPublisher
from utils.logger import get_logger

logger = get_logger()


class DummyEventPublisher(DomainEventPublisher):
    """Simple event publisher that prints events (for testing/demo purposes)."""

    async def publish(self, event: DomainEvent) -> None:
        await logger.info('Event published', event_data=event.model_dump(mode='json'))
