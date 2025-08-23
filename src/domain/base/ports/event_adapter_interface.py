import abc

from domain.base.event import DomainEvent


class DomainEventPublisher(abc.ABC):
    """Abstract base class for publishing domain events."""

    @abc.abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to the event bus or message broker."""
        raise NotImplementedError
