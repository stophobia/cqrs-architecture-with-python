import uuid

import pytest

from domain.payment.adapters.paypal_adapter import PayPalPaymentAdapter
from domain.payment.model.value_objects import PaymentId


@pytest.mark.asyncio
async def test_new_payment_returns_paymentid(monkeypatch):
    adapter = PayPalPaymentAdapter()

    fixed_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
    monkeypatch.setattr(uuid, 'uuid4', lambda: fixed_uuid)

    result = await adapter.new_payment(100.0)

    assert isinstance(result, PaymentId)
    assert str(result) == str(fixed_uuid)


@pytest.mark.asyncio
async def test_new_payment_generates_unique_ids():
    adapter = PayPalPaymentAdapter()
    result1 = await adapter.new_payment(50.0)
    result2 = await adapter.new_payment(75.0)

    assert isinstance(result1, PaymentId)
    assert isinstance(result2, PaymentId)
    assert result1 != result2  # cada pagamento gera um novo UUID


@pytest.mark.asyncio
async def test_verify_payment_always_true():
    adapter = PayPalPaymentAdapter()
    payment_id = PaymentId('dummy-id')

    result = await adapter.verify_payment(payment_id)

    assert result is True
