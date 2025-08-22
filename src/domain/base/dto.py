from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DataTransferObject(BaseModel):
    """Base class for Data Transfer Objects (DTOs)."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.model_dump() == other.model_dump()
