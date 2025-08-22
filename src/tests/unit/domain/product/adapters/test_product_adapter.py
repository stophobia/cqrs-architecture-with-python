import pytest

from domain.product.adapters.product_adapter import ProductAdapter
from domain.product.model.value_objects import ProductId


@pytest.mark.asyncio
async def test_total_price_empty_list():
    adapter = ProductAdapter()
    result = await adapter.total_price([])
    assert result == 0.0


@pytest.mark.asyncio
async def test_total_price_single_product():
    adapter = ProductAdapter()
    result = await adapter.total_price([(ProductId('p1'), 3)])
    assert result == 36.0


@pytest.mark.asyncio
async def test_total_price_multiple_products():
    adapter = ProductAdapter()
    products = [(ProductId('p1'), 2), (ProductId('p2'), 5), (ProductId('p3'), 1)]
    result = await adapter.total_price(products)
    assert result == 96.0


@pytest.mark.asyncio
async def test_total_price_zero_quantity():
    adapter = ProductAdapter()
    products = [(ProductId('p1'), 0), (ProductId('p2'), 4)]
    result = await adapter.total_price(products)
    assert result == 48.0
