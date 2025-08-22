from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Entity(BaseModel):
    """Base class for domain entities."""

    id: UUID = Field(default_factory=uuid4)
    version: int = 0

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def increase_version(self) -> None:
        """Increment the entity version."""
        self.version += 1

    def __str__(self) -> str:
        return f"{type(self).__name__}"

    def __repr__(self) -> str:
        return self.__str__()


class AggregateRoot(Entity):
    """Base class for domain aggregates (1+ entities)."""
