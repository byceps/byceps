from string import Template

import pytest

from byceps.blueprints.site.shop.payment.paypal.views import (
    _check_transaction_against_order,
    _extract_transaction_id,
)

from .helpers import json_to_obj


def test_paypal_extract_transaction_id():
    response = json_to_obj(
        """
        {
            "result": {
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "captures": [
                                {
                                    "id": "transaction-id-denied",
                                    "status": "DENIED"
                                },
                                {
                                    "id": "transaction-id-completed",
                                    "status": "COMPLETED"
                                }
                            ]
                        }
                    }
                ]
            }
        }
        """
    )

    assert _extract_transaction_id(response) == 'transaction-id-completed'


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

    response_json_template = Template(
        """
        {
            "result": {
                "status": "$status",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "$currency_code",
                            "value": "$total_amount"
                        },
                        "invoice_id": "$invoice_id"
                    }
                ]
            }
        }
        """
    )

    response_json = response_json_template.substitute(
        {
            'status': status,
            'currency_code': currency_code,
            'total_amount': total_amount,
            'invoice_id': invoice_id,
        }
    )
    response = json_to_obj(response_json)

    assert _check_transaction_against_order(response, order) == expected
