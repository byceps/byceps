"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
from flask_babel import force_locale
from moneyed import EUR, Money

from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.number import OrderNumber


def test_assemble_text_for_paid_order_to_orderer(app: Flask, build_paid_order):
    language_code = 'de'

    order_number = OrderNumber('EF-33-B00022')

    order = build_paid_order(
        created_at=datetime(2014, 9, 23, 18, 40, 53),
        order_number=order_number,
        line_items=[],
        total_amount=Money('57.11', EUR),
    )

    with force_locale(language_code):
        actual = order_email_service.assemble_text_for_paid_order_to_orderer(
            order
        )

    assert (
        actual.subject
        == '\u2705 Deine Bestellung (EF-33-B00022) ist bezahlt worden.'
    )
    assert (
        actual.body_main_part
        == '''
vielen Dank für deine Bestellung mit der Nummer EF-33-B00022 am 23.09.2014 über unsere Website.

Wir haben deine Zahlung erhalten und deine Bestellung als bezahlt markiert.
    '''.strip()
    )
