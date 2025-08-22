from __future__ import annotations

import abc

from domain.maps.model.value_objects import Address


class MapsAdapterInterface(abc.ABC):
    """Abstraction for maps and distance calculation integration."""

    @abc.abstractmethod
    async def calculate_distance_from_warehouses(self, destination: Address) -> float:
        """Calculate the distance from available warehouses to a destination address."""
        raise NotImplementedError()
