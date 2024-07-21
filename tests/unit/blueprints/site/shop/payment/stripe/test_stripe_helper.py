"""
:Copyright: 2020 Micha Ober
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from moneyed import EUR, Money
import pytest

from byceps.blueprints.site.shop.payment.stripe.views import (
    _check_transaction_against_order,
)
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import (
    Address,
    Order,
    Orderer,
    OrderID,
    OrderState,
    PaymentState,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID

from tests.helpers import generate_token, generate_uuid


@pytest.mark.parametrize(
    'payment_status, currency, amount_total, order_number, expected_result',
    [
        ('paid', 'eur', 4711, 'order-001', True),
        ('paid', 'eur', 5711, 'order-001', False),
        ('paid', 'usd', 4711, 'order-001', False),
        ('paid', 'eur', 4711, 'order-002', False),
        ('unpaid', 'eur', 4711, 'order-001', False),
        ('no_payment_required', 'eur', 4711, 'order-001', False),
    ],
)
def test_stripe_check_transaction(
    orderer: Orderer,
    payment_status: str,
    currency: str,
    amount_total: int,
    order_number: str,
    expected_result: bool,
) -> None:
    order = create_order(
        OrderNumber('order-001'), orderer, Money(Decimal('47.11'), EUR)
    )

    response = SimpleNamespace(
        payment_status=payment_status,
        currency=currency,
        amount_total=amount_total,
        metadata={'order_number': order_number},
    )

    assert _check_transaction_against_order(response, order) == expected_result


def create_order(
    order_number: OrderNumber, orderer: Orderer, total_amount: Money
) -> Order:
    return Order(
        id=OrderID(generate_uuid()),
        created_at=datetime.utcnow(),
        shop_id=ShopID(generate_token()),
        storefront_id=StorefrontID(generate_token()),
        order_number=order_number,
        placed_by=orderer.user,
        company=orderer.company,
        first_name=orderer.first_name,
        last_name=orderer.last_name,
        address=Address(
            country=orderer.country,
            zip_code=orderer.zip_code,
            city=orderer.city,
            street=orderer.street,
        ),
        line_items=[],
        total_amount=total_amount,
        is_invoiced=False,
        payment_method=None,
        payment_state=PaymentState.open,
        cancellation_reason=None,
        is_processing_required=False,
        is_processed=False,
        is_open=True,
        is_canceled=False,
        is_paid=False,
        is_overdue=False,
        state=OrderState.open,
    )
