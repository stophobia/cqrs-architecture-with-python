from __future__ import annotations

from datetime import datetime as dt
from typing import Any
from uuid import UUID, uuid4

from pydantic import ConfigDict, Field

from domain.base.entity import Entity


class DomainEvent(Entity):
    """Base class for domain events."""

    event_name: str
    tracker_id: UUID = Field(default_factory=uuid4)
    datetime: dt = Field(default_factory=dt.now)
    aggregate: Any

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @classmethod
    def domain_event_name(cls) -> str:
        """Return the domain event name (defaults to class name)."""
        return cls.__name__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.model_dump() == other.model_dump()
