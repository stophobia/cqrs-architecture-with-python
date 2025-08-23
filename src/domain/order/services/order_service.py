from typing import Annotated

from domain.maps.model.value_objects import Address
from domain.order.model.entities import Order
from domain.order.model.events import OrderCancelled, OrderCreated, OrderPaid
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.ports.order_service_interface import OrderServiceInterface
from utils.logger import get_logger

logger = get_logger()


class OrderService(OrderServiceInterface):
    """Application service responsible for orchestrating order operations."""

    async def create_new_order(
        self,
        buyer_id: Annotated[str, BuyerId],
        items: list[OrderItem],
        destination: Address,
    ) -> OrderId:
        """Create a new order with payment, product and delivery costs, then publish an event."""
        product_counts = [(item.product_id, int(item.amount)) for item in items]
        total_product_cost = await self.product_service.total_price(product_counts)
        payment_id = await self.payment_service.new_payment(total_product_cost)
        delivery_cost = await self.delivery_service.calculate_cost(total_product_cost, destination)

        order = Order(
            buyer_id=buyer_id,
            items=items,
            product_cost=float(total_product_cost),
            delivery_cost=float(delivery_cost),
            payment_id=payment_id,
        )
        await self.repository.save(order)
        await self.event_publisher.publish(OrderCreated(aggregate=order))
        await logger.info(
            'Order created',
            order_id=str(order.id),
            buyer_id=str(buyer_id),
            payment_id=str(payment_id),
        )
        return OrderId(order.id)

    async def pay_order(self, order_id: Annotated[str, OrderId]) -> None:
        """Verify payment and mark the order as paid, then publish an event."""
        order = await self.repository.from_id(order_id=order_id)
        is_payment_verified = await self.payment_service.verify_payment(payment_id=order.payment_id)
        await self._pay_order_tnx(order_id, is_payment_verified)
        await logger.info(
            'Order paid',
            order_id=str(order_id),
            payment_verified=is_payment_verified,
        )

    async def cancel_order(self, order_id: Annotated[str, OrderId]) -> None:
        """Cancel an order and publish an event."""
        order = await self.repository.from_id(order_id)
        order.cancel()
        await self.repository.save(order)
        await self.event_publisher.publish(OrderCancelled(aggregate=order))
        await logger.info(
            'Order cancelled',
            order_id=str(order_id),
            status=order.status,
        )

    async def _pay_order_tnx(
        self, order_id: Annotated[str, OrderId], is_payment_verified: bool
    ) -> None:
        """Transaction helper for paying an order and publishing an event."""
        order = await self.repository.from_id(order_id=order_id)
        order.pay(is_payment_verified=is_payment_verified)
        await self.repository.save(order)
        await self.event_publisher.publish(OrderPaid(aggregate=order))

    async def get_order_from_id(self, order_id: Annotated[str, OrderId]) -> Order:
        """Retrieve an order by its identifier."""
        order = await self.repository.from_id(order_id)
        await logger.info('Order retrieved', order_id=order_id)
        return order
