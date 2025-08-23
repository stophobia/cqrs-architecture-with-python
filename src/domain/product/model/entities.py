from decimal import Decimal

from domain.base.entity import Entity
from domain.product.model.value_objects import ProductId


class Product(Entity):
    """Entity representing a product."""

    product_id: ProductId
    price: Decimal
