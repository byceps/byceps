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


def test_assemble_text_for_canceled_order_to_orderer(
    app: Flask, build_canceled_order
):
    language_code = 'de'

    order_number = OrderNumber('CD-22-B00017')

    order = build_canceled_order(
        created_at=datetime(2014, 11, 5, 23, 32, 9),
        order_number=order_number,
        line_items=[],
        total_amount=Money('57.11', EUR),
        cancelation_reason='Du hast nicht rechtzeitig bezahlt.',
    )

    with force_locale(language_code):
        actual = (
            order_email_service.assemble_text_for_canceled_order_to_orderer(
                order
            )
        )

    assert (
        actual.subject
        == '\u274c Deine Bestellung (CD-22-B00017) ist storniert worden.'
    )
    assert (
        actual.body_main_part
        == '''
deine Bestellung mit der Nummer CD-22-B00017 vom 06.11.2014 wurde von uns aus folgendem Grund storniert:

Du hast nicht rechtzeitig bezahlt.
    '''.strip()
    )
