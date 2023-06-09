"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
from flask_babel import force_locale
from moneyed import EUR, Money

from byceps.services.shop.article.models import ArticleNumber
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.number import OrderNumber


def test_assemble_text_for_incoming_order_to_orderer(
    app: Flask, build_line_item, build_open_order
):
    language_code = 'de'

    order_number = OrderNumber('AB-11-B00253')

    line_items = [
        build_line_item(
            order_number=order_number,
            article_number=ArticleNumber('AB-11-A00003'),
            description='Einzelticket, Kategorie Loge',
            unit_price=Money('99.00', EUR),
            quantity=5,
            line_amount=Money('495.00', EUR),
        ),
        build_line_item(
            order_number=order_number,
            article_number=ArticleNumber('AB-11-A00007'),
            description='T-Shirt, Größe L',
            unit_price=Money('14.95', EUR),
            quantity=2,
            line_amount=Money('29.90', EUR),
        ),
    ]

    order = build_open_order(
        created_at=datetime(2014, 8, 15, 20, 7, 43),
        order_number=order_number,
        line_items=line_items,
        total_amount=Money('524.90', EUR),
    )

    payment_instructions = '''
Bitte überweise den Gesamtbetrag auf dieses Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AB-11-B00253

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.yourparty.example/shop/orders
    '''.strip()

    with force_locale(language_code):
        actual = (
            order_email_service.assemble_text_for_incoming_order_to_orderer(
                order, payment_instructions
            )
        )

    assert actual.subject == 'Deine Bestellung (AB-11-B00253) ist eingegangen.'
    assert (
        actual.body_main_part
        == '''
vielen Dank für deine Bestellung mit der Nummer AB-11-B00253 am 15.08.2014 über unsere Website.

Folgende Artikel hast du bestellt:

  Beschreibung: Einzelticket, Kategorie Loge
  Anzahl: 5
  Stückpreis: 99,00\xa0€
  Zeilenpreis: 495,00\xa0€

  Beschreibung: T-Shirt, Größe L
  Anzahl: 2
  Stückpreis: 14,95\xa0€
  Zeilenpreis: 29,90\xa0€

  Gesamtbetrag: 524,90\xa0€

Bitte überweise den Gesamtbetrag auf dieses Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AB-11-B00253

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.yourparty.example/shop/orders
    '''.strip()
    )
