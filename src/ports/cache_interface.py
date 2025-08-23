import abc
from typing import Any


class CacheInterface(abc.ABC):
    """Abstraction for cache storage implementations."""

    def __init__(self, silent_mode: bool = False) -> None:
        self.silent_mode = silent_mode

    @abc.abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve a value from the cache by key."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def set(self, key: str, data: dict[str, Any], ttl: int) -> None:
        """Set a value in the cache with a time-to-live (ttl)."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value from the cache by key."""
        raise NotImplementedError()
