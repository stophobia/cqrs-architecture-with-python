# pylint: disable=redefined-outer-name
from unittest.mock import AsyncMock

import pytest

from domain.delivery.adapters.cost_calculator_adapter import (
    BASE_PRICE,
    FLAT_PRICE,
    FREE,
    FREE_DISTANCE_THRESHOLD,
    ORDER_PRICE_THRESHOLD,
    PRICE_PER_EXTRA_DISTANCE,
    DeliveryCostCalculatorAdapter,
)
from domain.maps.model.value_objects import Address, StatesEnum


@pytest.fixture
def mock_address():
    return Address(
        house_number='70',
        road='Rua A',
        sub_district='Bairro X',
        district='Cidade Y',
        state=StatesEnum.SP,
        postcode='12345-678',
        country='Brasil',
    )


@pytest.mark.asyncio
async def test_large_order_free_within_threshold(mock_address):
    maps_service = AsyncMock()
    maps_service.calculate_distance_from_warehouses.return_value = FREE_DISTANCE_THRESHOLD
    adapter = DeliveryCostCalculatorAdapter(maps_service)

    result = await adapter.calculate_cost(ORDER_PRICE_THRESHOLD, mock_address)
    assert result == FREE
    maps_service.calculate_distance_from_warehouses.assert_awaited_once()


@pytest.mark.asyncio
async def test_large_order_flat_price_beyond_threshold(mock_address):
    maps_service = AsyncMock()
    maps_service.calculate_distance_from_warehouses.return_value = FREE_DISTANCE_THRESHOLD + 10
    adapter = DeliveryCostCalculatorAdapter(maps_service)

    result = await adapter.calculate_cost(ORDER_PRICE_THRESHOLD + 100, mock_address)
    assert result == FLAT_PRICE


@pytest.mark.asyncio
async def test_small_order_base_price_within_threshold(mock_address):
    maps_service = AsyncMock()
    maps_service.calculate_distance_from_warehouses.return_value = FREE_DISTANCE_THRESHOLD
    adapter = DeliveryCostCalculatorAdapter(maps_service)

    result = await adapter.calculate_cost(ORDER_PRICE_THRESHOLD - 1, mock_address)
    assert result == BASE_PRICE


@pytest.mark.asyncio
async def test_small_order_with_extra_distance(mock_address):
    maps_service = AsyncMock()
    distance = FREE_DISTANCE_THRESHOLD + 5
    maps_service.calculate_distance_from_warehouses.return_value = distance
    adapter = DeliveryCostCalculatorAdapter(maps_service)

    result = await adapter.calculate_cost(ORDER_PRICE_THRESHOLD - 1, mock_address)
    expected = BASE_PRICE + PRICE_PER_EXTRA_DISTANCE * (distance - FREE_DISTANCE_THRESHOLD)
    assert result == expected


@pytest.mark.asyncio
async def test_large_order_exactly_at_threshold_distance(mock_address):
    maps_service = AsyncMock()
    maps_service.calculate_distance_from_warehouses.return_value = FREE_DISTANCE_THRESHOLD
    adapter = DeliveryCostCalculatorAdapter(maps_service)

    result = await adapter.calculate_cost(ORDER_PRICE_THRESHOLD + 50, mock_address)
    assert result == FREE


@pytest.mark.asyncio
async def test_small_order_exactly_at_threshold_distance(mock_address):
    maps_service = AsyncMock()
    maps_service.calculate_distance_from_warehouses.return_value = FREE_DISTANCE_THRESHOLD
    adapter = DeliveryCostCalculatorAdapter(maps_service)

    result = await adapter.calculate_cost(ORDER_PRICE_THRESHOLD - 100, mock_address)
    assert result == BASE_PRICE
