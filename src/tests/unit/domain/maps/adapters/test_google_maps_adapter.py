import pytest

from domain.maps.adapters.google_maps_adapter import GoogleMapsAdapter
from domain.maps.model.value_objects import Address, StatesEnum


def make_address(house_number) -> Address:
    return Address(
        house_number=house_number,
        road='Rua A',
        sub_district='Bairro X',
        district='Cidade Y',
        state=StatesEnum.SP,
        postcode='12345-678',
        country='Brasil',
    )


@pytest.mark.asyncio
async def test_calculate_distance_valid_integer_house_number():
    adapter = GoogleMapsAdapter()
    destination = make_address(25)
    result = await adapter.calculate_distance_from_warehouses(destination)
    assert result == 25.0


@pytest.mark.asyncio
async def test_calculate_distance_valid_string_house_number():
    adapter = GoogleMapsAdapter()
    destination = make_address('42')
    result = await adapter.calculate_distance_from_warehouses(destination)
    assert result == 42.0


@pytest.mark.asyncio
async def test_calculate_distance_with_fraction_house_number():
    adapter = GoogleMapsAdapter()
    destination = make_address('100/2')
    result = await adapter.calculate_distance_from_warehouses(destination)
    assert result == 100.0


@pytest.mark.asyncio
async def test_calculate_distance_invalid_house_number_valueerror():
    adapter = GoogleMapsAdapter()
    destination = make_address('ABC')
    result = await adapter.calculate_distance_from_warehouses(destination)
    assert result == 0.0


@pytest.mark.asyncio
async def test_calculate_distance_none_house_number_typeerror():
    adapter = GoogleMapsAdapter()
    destination = make_address(None)
    result = await adapter.calculate_distance_from_warehouses(destination)
    assert result == 0.0
