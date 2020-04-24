"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from byceps.services.shop.article import service as article_service
from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.snippet import service as snippet_service

from tests.helpers import create_user_with_detail, current_user_set
from tests.services.shop.helpers import (
    create_article as _create_article,
    create_shop_fragment,
)

from .base import place_order_with_items


@pytest.fixture
def customer(party_app):
    return create_user_with_detail(
        'Interessent', email_address='interessent@example.com'
    )


@pytest.fixture
def article1(shop):
    article = create_article(
        shop.id,
        'AC-14-A00003',
        'Einzelticket, Kategorie Loge',
        Decimal('99.00'),
        123,
    )
    article_id = article.id

    yield article

    article_service.delete_article(article_id)


@pytest.fixture
def article2(shop):
    article = create_article(
        shop.id,
        'AC-14-A00007',
        'T-Shirt, Größe L',
        Decimal('14.95'),
        50,
    )
    article_id = article.id

    yield article

    article_service.delete_article(article_id)


@pytest.fixture
def order(shop, article1, article2, customer, order_admin):
    sequence_service.create_order_number_sequence(shop.id, 'AC-14-B', value=252)

    email_payment_instructions_snippet_id = create_email_payment_instructions_snippet(
        shop.id, order_admin.id
    )
    email_footer_snippet_id = create_email_footer_snippet(
        shop.id, order_admin.id
    )

    created_at = datetime(2014, 8, 15, 20, 7, 43)

    items_with_quantity = [
        (article1, 5),
        (article2, 2),
    ]

    order = place_order_with_items(
        shop.id, customer, created_at, items_with_quantity
    )

    yield order

    snippet_service.delete_snippet(email_payment_instructions_snippet_id)
    snippet_service.delete_snippet(email_footer_snippet_id)
    order_service.delete_order(order.id)
    sequence_service.delete_order_number_sequence(shop.id)


@patch('byceps.email.send')
def test_email_on_order_placed(send_email_mock, party_app, customer, order):
    app = party_app

    with current_user_set(app, customer), app.app_context():
        order_email_service.send_email_for_incoming_order_to_orderer(order.id)

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


# helpers


def create_email_payment_instructions_snippet(shop_id, admin_id):
    return create_shop_fragment(
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
    return create_shop_fragment(
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


def create_article(shop_id, item_number, description, price, quantity):
    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        quantity=quantity,
    )
