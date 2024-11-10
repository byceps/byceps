from paypalhttp import HttpResponse
import pytest

from byceps.blueprints.site.shop.payment.paypal.views import (
    PayPalOrderDetails,
    _check_transaction_against_order,
    _parse_paypal_order_details,
)

from .helpers import json_to_obj


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
        ('COMPLETED', 'EUR', '47.11', 'order-001', True),
        ('COMPLETED', 'EUR', '57.11', 'order-001', False),
        ('DENIED', 'EUR', '47.11', 'order-001', False),
        ('COMPLETED', 'USD', '47.11', 'order-001', False),
        ('COMPLETED', 'EUR', '47.11', 'order-002', False),
    ],
)
def test_paypal_check_transaction_against_order(
    status, currency_code, total_amount, invoice_id, expected
):
    order = json_to_obj(
        """
        {
            "total_amount": "47.11",
            "order_number": "order-001"
        }
        """
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
