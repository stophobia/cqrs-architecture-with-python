from domain.delivery.ports.cost_calculator_interface import DeliveryCostCalculatorAdapterInterface
from domain.maps.model.value_objects import Address
from domain.maps.ports.maps_adapter_interface import MapsAdapterInterface

ORDER_PRICE_THRESHOLD: float = 500.0
FREE_DISTANCE_THRESHOLD: float = 30.0
FREE: float = 0.0
FLAT_PRICE: float = 50.0
BASE_PRICE: float = 50.0
PRICE_PER_EXTRA_DISTANCE: float = 15.0


class DeliveryCostCalculatorAdapter(DeliveryCostCalculatorAdapterInterface):
    """Delivery cost calculator using distance and product cost thresholds."""

    def __init__(self, maps_service: MapsAdapterInterface) -> None:
        self.maps_service = maps_service

    async def calculate_cost(self, total_product_cost: float, destination: Address) -> float:
        """Decide whether to calculate cost as a large or small delivery."""
        if total_product_cost >= ORDER_PRICE_THRESHOLD:
            return await self._large_delivery_calculate_cost(destination)
        return await self._small_delivery_calculate_cost(destination)

    async def _large_delivery_calculate_cost(self, destination: Address) -> float:
        """Calculate delivery cost for large orders."""
        distance = await self.maps_service.calculate_distance_from_warehouses(destination)
        if distance <= FREE_DISTANCE_THRESHOLD:
            return FREE
        return FLAT_PRICE

    async def _small_delivery_calculate_cost(self, destination: Address) -> float:
        """Calculate delivery cost for small orders."""
        distance = await self.maps_service.calculate_distance_from_warehouses(destination)
        if distance <= FREE_DISTANCE_THRESHOLD:
            return BASE_PRICE

        distance_extra = distance - FREE_DISTANCE_THRESHOLD
        return BASE_PRICE + PRICE_PER_EXTRA_DISTANCE * distance_extra
