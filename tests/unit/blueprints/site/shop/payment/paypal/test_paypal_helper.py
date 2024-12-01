from datetime import datetime
from decimal import Decimal

from moneyed import EUR, Money
from paypalhttp import HttpResponse
import pytest

from byceps.blueprints.site.shop.payment.paypal.views import (
    PayPalOrderDetails,
    _check_transaction_against_order,
    _parse_paypal_order_details,
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
from byceps.util.result import Err, Ok, Result

from tests.helpers import generate_token, generate_uuid


def test_parse_paypal_order_details():
    expected = PayPalOrderDetails(
        id='1DA59471B5379105V',
        transaction_id='transaction-id-completed',
    )

    result_data = {
        'id': '1DA59471B5379105V',
        'status': 'COMPLETED',
        'purchase_units': [
            {
                'payments': {
                    'captures': [
                        {
                            'id': 'transaction-id-denied',
                            'status': 'DENIED',
                        },
                        {
                            'id': 'transaction-id-completed',
                            'status': 'COMPLETED',
                        },
                    ],
                },
            },
        ],
    }

    result = HttpResponse(result_data, 200).result

    assert _parse_paypal_order_details(result) == expected


@pytest.mark.parametrize(
    'status, currency_code, total_amount, invoice_id, expected',
    [
        ('COMPLETED', 'EUR', '47.11', 'order-001', Ok(None)),
        ('DENIED', 'EUR', '47.11', 'order-001', Err({'status'})),
        ('COMPLETED', 'EUR', '57.11', 'order-001', Err({'total_amount'})),
        ('COMPLETED', 'USD', '47.11', 'order-001', Err({'currency_code'})),
        ('COMPLETED', 'EUR', '47.11', 'order-002', Err({'invoice_id'})),
    ],
)
def test_paypal_check_transaction_against_order(
    orderer: Orderer,
    status: str,
    currency_code: str,
    total_amount: str,
    invoice_id: str,
    expected: Result[None, set[str]],
):
    order = create_order(
        OrderNumber('order-001'), orderer, Money(Decimal('47.11'), EUR)
    )

    result_data = {
        'status': status,
        'purchase_units': [
            {
                'amount': {
                    'currency_code': currency_code,
                    'value': total_amount,
                },
                'invoice_id': invoice_id,
            },
        ],
    }

    result = HttpResponse(result_data, 200).result

    assert _check_transaction_against_order(result, order) == expected


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
