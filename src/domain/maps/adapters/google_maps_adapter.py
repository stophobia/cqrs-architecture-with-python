from __future__ import annotations

from domain.maps.model.value_objects import Address
from domain.maps.ports.maps_adapter_interface import MapsAdapterInterface


class GoogleMapsAdapter(MapsAdapterInterface):
    """Mock Google Maps adapter for distance calculation."""

    async def calculate_distance_from_warehouses(self, destination: Address) -> float:
        """Simulate a distance calculation using the house number as a proxy."""
        try:
            house_number = str(destination.house_number).split('/', maxsplit=1)[0]
            return float(house_number)
        except Exception:
            return 0.0
