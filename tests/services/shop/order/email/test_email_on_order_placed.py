"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.sequence import service as sequence_service

from tests.helpers import create_user_with_detail, current_user_set
from tests.services.shop.helpers import (
    create_article as _create_article,
    create_shop_fragment,
)

from .base import place_order_with_items


@patch('byceps.email.send')
def test_email_on_order_placed(
    send_email_mock, party_app_with_db, shop, order_admin
):
    app = party_app_with_db

    user = create_user_with_detail(
        'Interessent', email_address='interessent@example.com'
    )

    sequence_service.create_order_number_sequence(shop.id, 'AC-14-B', value=252)
    create_email_payment_instructions_snippet(shop.id, order_admin.id)
    create_email_footer_snippet(shop.id, order_admin.id)

    order_id = place_order(shop.id, user)

    with current_user_set(app, user), app.app_context():
        order_email_service.send_email_for_incoming_order_to_orderer(order_id)

    expected_to_orderer_sender = 'info@shop.example'
    expected_to_orderer_recipients = ['interessent@example.com']
    expected_to_orderer_subject = (
        'Deine Bestellung (AC-14-B00253) ist eingegangen.'
    )
    expected_to_orderer_body = '''
Hallo Interessent,

vielen Dank für deine Bestellung mit der Nummer AC-14-B00253 am 15.08.2014 über unsere Website.

Folgende Artikel hast du bestellt:

  Bezeichnung: Einzelticket, Kategorie Loge
  Anzahl: 5
  Stückpreis: 99,00 €

  Bezeichnung: T-Shirt, Größe L
  Anzahl: 2
  Stückpreis: 14,95 €

  Gesamtbetrag: 524,90 €

Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AC-14-B00253

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.example.com/shop/orders

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: acmecon@example.com
    '''.strip()

    send_email_mock.assert_called_once_with(
        expected_to_orderer_sender,
        expected_to_orderer_recipients,
        expected_to_orderer_subject,
        expected_to_orderer_body,
    )


def create_email_payment_instructions_snippet(shop_id, admin_id):
    create_shop_fragment(
        shop_id,
        admin_id,
        'email_payment_instructions',
        '''
Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: {{ order_number }}

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.example.com/shop/orders
''',
    )


def create_email_footer_snippet(shop_id, admin_id):
    create_shop_fragment(
        shop_id,
        admin_id,
        'email_footer',
        '''
Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: acmecon@example.com
''',
    )


def place_order(shop_id, user):
    created_at = datetime(2014, 8, 15, 20, 7, 43)

    article1 = create_article(
        shop_id,
        'AC-14-A00003',
        'Einzelticket, Kategorie Loge',
        Decimal('99.00'),
        123,
    )
    article2 = create_article(
        shop_id,
        'AC-14-A00007',
        'T-Shirt, Größe L',
        Decimal('14.95'),
        50,
    )

    items_with_quantity = [
        (article1, 5),
        (article2, 2),
    ]

    return place_order_with_items(
        shop_id, user, created_at, items_with_quantity
    )


def create_article(shop_id, item_number, description, price, quantity):
    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        quantity=quantity,
    )
