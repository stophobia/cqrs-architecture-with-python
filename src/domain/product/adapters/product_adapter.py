from collections.abc import Sequence

from domain.product.model.value_objects import ProductId
from domain.product.ports.product_adapter_interface import ProductAdapterInterface


class ProductAdapter(ProductAdapterInterface):
    """Mock product adapter for calculating total price."""

    async def total_price(self, product_counts: Sequence[tuple[ProductId, int]]) -> float:
        """Return total price given a sequence of product/count tuples."""
        return float(sum(12.0 * count for _, count in product_counts))
