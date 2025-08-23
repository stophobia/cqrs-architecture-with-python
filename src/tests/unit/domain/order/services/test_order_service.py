# pylint: disable=redefined-outer-name, protected-access
from unittest.mock import MagicMock

import pytest

from adapters.event_publisher_adapter import DummyEventPublisher
from domain.delivery.adapters.cost_calculator_adapter import (
    DeliveryCostCalculatorAdapter,
)
from domain.maps.model.value_objects import Address
from domain.order.exceptions.order_exceptions import (
    OrderAlreadyCancelledException,
    OrderAlreadyPaidException,
    PaymentNotVerifiedException,
)
from domain.order.model.entities import Order
from domain.order.model.events import OrderCancelled, OrderPaid
from domain.order.model.value_objects import BuyerId, OrderId, OrderItem
from domain.order.repositories.order_repository import (
    OrderRepository,
)
from domain.order.services.order_service import OrderService
from domain.payment.adapters.paypal_adapter import PayPalPaymentAdapter
from domain.product.adapters.product_adapter import ProductAdapter


@pytest.fixture
def order_service():
    return OrderService(
        repository=MagicMock(spec=OrderRepository),
        payment_service=MagicMock(spec=PayPalPaymentAdapter),
        product_service=MagicMock(spec=ProductAdapter),
        delivery_service=MagicMock(spec=DeliveryCostCalculatorAdapter),
        event_publisher=MagicMock(spec=DummyEventPublisher()),
    )


@pytest.mark.asyncio
async def test_create_new_order(order_service):
    items = [OrderItem(product_id='p1', amount=2)]
    order_service.product_service.total_price.return_value = 100
    order_service.payment_service.new_payment.return_value = 'pay123'
    order_service.delivery_service.calculate_cost.return_value = 10

    order_id = await order_service.create_new_order(
        buyer_id=BuyerId('b1'),
        items=items,
        destination=Address(
            house_number='S/N',
            road='Rua A',
            sub_district='Bairro X',
            district='Cidade Y',
            state='Rio Grande do Sul',
            postcode='12345-678',
            country='Brasil',
        ),
    )

    order_service.product_service.total_price.assert_called_once()
    order_service.payment_service.new_payment.assert_called_once_with(100)
    order_service.delivery_service.calculate_cost.assert_called_once()
    order_service.repository.save.assert_awaited()
    order_service.event_publisher.publish.assert_awaited()
    assert isinstance(order_id, OrderId)


@pytest.mark.asyncio
async def test_pay_order(order_service):
    fake_order = MagicMock(spec=Order)
    fake_order.payment_id = 'pay123'
    order_service.repository.from_id.return_value = fake_order
    order_service.payment_service.verify_payment.return_value = True

    await order_service.pay_order(order_id=OrderId('o1'))

    order_service.repository.from_id.assert_awaited_with(order_id='o1')
    order_service.payment_service.verify_payment.assert_awaited_with(payment_id='pay123')
    order_service.repository.save.assert_awaited()
    order_service.event_publisher.publish.assert_awaited()
    published_event = order_service.event_publisher.publish.call_args.args[0]
    assert isinstance(published_event, OrderPaid)


@pytest.mark.asyncio
async def test_cancel_order(order_service):
    fake_order = MagicMock(spec=Order)
    order_service.repository.from_id.return_value = fake_order

    await order_service.cancel_order(order_id=OrderId('o2'))

    fake_order.cancel.assert_called_once()
    order_service.repository.save.assert_awaited_with(fake_order)
    published_event = order_service.event_publisher.publish.call_args.args[0]
    assert isinstance(published_event, OrderCancelled)


@pytest.mark.asyncio
async def test__pay_order_tnx(order_service):
    fake_order = MagicMock(spec=Order)
    order_service.repository.from_id.return_value = fake_order

    await order_service._pay_order_tnx(order_id=OrderId('o3'), is_payment_verified=True)

    fake_order.pay.assert_called_once_with(is_payment_verified=True)
    order_service.repository.save.assert_awaited_with(fake_order)
    published_event = order_service.event_publisher.publish.call_args.args[0]
    assert isinstance(published_event, OrderPaid)


@pytest.mark.asyncio
async def test_get_order_from_id(order_service):
    fake_order = MagicMock(spec=Order)
    order_service.repository.from_id.return_value = fake_order

    result = await order_service.get_order_from_id(order_id=OrderId('o4'))

    order_service.repository.from_id.assert_awaited_with('o4')
    assert result is fake_order


@pytest.mark.asyncio
async def test__pay_order_tnx_raises_if_order_already_cancelled(order_service):
    order = Order(
        buyer_id=BuyerId('b1'),
        items=[OrderItem(product_id='p1', amount=1)],
        product_cost=100,
        delivery_cost=10,
        payment_id='pay123',
    )
    order.cancel()
    order_service.repository.from_id.return_value = order

    with pytest.raises(OrderAlreadyCancelledException):
        await order_service._pay_order_tnx(order_id=order.id, is_payment_verified=True)


@pytest.mark.asyncio
async def test__pay_order_tnx_raises_if_order_already_paid(order_service):
    order = Order(
        buyer_id=BuyerId('b1'),
        items=[OrderItem(product_id='p1', amount=1)],
        product_cost=100,
        delivery_cost=10,
        payment_id='pay123',
    )
    order.status = order.status.PAID
    order_service.repository.from_id.return_value = order

    with pytest.raises(OrderAlreadyPaidException):
        await order_service._pay_order_tnx(order_id=order.id, is_payment_verified=True)


@pytest.mark.asyncio
async def test__pay_order_tnx_raises_if_payment_not_verified(order_service):
    order = Order(
        buyer_id=BuyerId('b1'),
        items=[OrderItem(product_id='p1', amount=1)],
        product_cost=100,
        delivery_cost=10,
        payment_id='pay123',
    )
    order_service.repository.from_id.return_value = order

    with pytest.raises(PaymentNotVerifiedException):
        await order_service._pay_order_tnx(order_id=order.id, is_payment_verified=False)


@pytest.mark.asyncio
async def test_cancel_order_raises_if_already_cancelled(order_service):
    order = Order(
        buyer_id=BuyerId('b1'),
        items=[OrderItem(product_id='p1', amount=1)],
        product_cost=100,
        delivery_cost=10,
        payment_id='pay123',
    )
    order.cancel()
    order_service.repository.from_id.return_value = order

    with pytest.raises(OrderAlreadyCancelledException):
        await order_service.cancel_order(order_id=order.id)


@pytest.mark.asyncio
async def test_cancel_order_raises_if_already_paid(order_service):
    order = Order(
        buyer_id=BuyerId('b1'),
        items=[OrderItem(product_id='p1', amount=1)],
        product_cost=100,
        delivery_cost=10,
        payment_id='pay123',
    )
    order.status = order.status.PAID
    order_service.repository.from_id.return_value = order

    with pytest.raises(OrderAlreadyPaidException):
        await order_service.cancel_order(order_id=order.id)
