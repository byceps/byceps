"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from byceps.services.shop.article import service as article_service
from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
    service as order_service,
)
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.snippet import service as snippet_service

from tests.helpers import current_user_set
from tests.integration.services.shop.helpers import (
    create_article as _create_article,
    create_shop_fragment,
)

from .helpers import place_order_with_items


@pytest.fixture(scope='package')
def order_admin(make_user):
    return make_user('PlacedEmailShopOrderAdmin')


@pytest.fixture(scope='module')
def customer(make_user_with_detail):
    return make_user_with_detail(
        'Interessent', email_address='interessent@users.test'
    )


@pytest.fixture
def order_number_sequence_id(shop) -> None:
    sequence_id = order_sequence_service.create_order_number_sequence(
        shop.id, 'AC-14-B', value=252
    )

    yield sequence_id

    order_sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture
def storefront(shop, order_number_sequence_id) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront',
        shop.id,
        order_number_sequence_id,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


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
def order(storefront, article1, article2, customer, order_admin):
    email_payment_instructions_snippet_id = create_email_payment_instructions_snippet(
        storefront.shop_id, order_admin.id
    )
    email_footer_snippet_id = create_email_footer_snippet(
        storefront.shop_id, order_admin.id
    )

    created_at = datetime(2014, 8, 15, 20, 7, 43)

    items_with_quantity = [
        (article1, 5),
        (article2, 2),
    ]

    order = place_order_with_items(
        storefront.id, customer, created_at, items_with_quantity
    )

    yield order

    snippet_service.delete_snippet(email_payment_instructions_snippet_id)
    snippet_service.delete_snippet(email_footer_snippet_id)
    order_service.delete_order(order.id)


@patch('byceps.email.send')
def test_email_on_order_placed(send_email_mock, site_app, customer, order):
    app = site_app

    with current_user_set(app, customer), app.app_context():
        order_email_service.send_email_for_incoming_order_to_orderer(order.id)

    expected_to_orderer_sender = 'noreply@acmecon.test'
    expected_to_orderer_recipients = ['interessent@users.test']
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

Hier kannst du deine Bestellungen einsehen: https://www.acmecon.test/shop/orders

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
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

Hier kannst du deine Bestellungen einsehen: https://www.acmecon.test/shop/orders
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

E-Mail: noreply@acmecon.test
''',
    )


def create_article(shop_id, item_number, description, price, total_quantity):
    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        total_quantity=total_quantity,
    )
