from domain.base.event import DomainEvent
from domain.base.ports.event_adapter_interface import DomainEventPublisher


class DummyEventPublisher(DomainEventPublisher):
    """Simple event publisher that prints events (for testing/demo purposes)."""

    async def publish(self, event: DomainEvent) -> None:
        print(event.model_dump_json(indent=2))
