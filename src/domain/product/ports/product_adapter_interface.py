import abc
from collections.abc import Sequence

from domain.product.model.value_objects import ProductId


class ProductAdapterInterface(abc.ABC):
    """Abstraction for product provider integration."""

    @abc.abstractmethod
    async def total_price(self, product_counts: Sequence[tuple[ProductId, int]]) -> float:
        """Calculate the total price for a sequence of product/count tuples."""
        raise NotImplementedError()
