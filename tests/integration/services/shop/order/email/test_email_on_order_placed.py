"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.shop.transfer.models import Shop, ShopID
from byceps.services.shop.storefront.transfer.models import Storefront
from byceps.services.snippet import service as snippet_service

from tests.helpers import current_user_set
from tests.integration.services.shop.helpers import (
    create_article as _create_article,
)

from .helpers import (
    assert_email,
    get_current_user_for_user,
    place_order_with_items,
)


@pytest.fixture(scope='module')
def customer(make_user):
    return make_user('Interessent', email_address='interessent@users.test')


@pytest.fixture
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='AB-11-B', value=252
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def article1(shop: Shop) -> Article:
    return create_article(
        shop.id,
        'AB-11-A00003',
        'Einzelticket, Kategorie Loge',
        Decimal('99.00'),
        123,
    )


@pytest.fixture
def article2(shop: Shop) -> Article:
    return create_article(
        shop.id,
        'AB-11-A00007',
        'T-Shirt, Größe L',
        Decimal('14.95'),
        50,
    )


@pytest.fixture
def order(
    storefront,
    article1: Article,
    article2: Article,
    customer,
    email_payment_instructions_snippet_id,
    email_footer_snippet_id,
):
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

    current_user = get_current_user_for_user(customer, 'de')
    with current_user_set(app, current_user), app.app_context():
        order_email_service.send_email_for_incoming_order_to_orderer(order.id)

    expected_sender = 'noreply@acmecon.test'
    expected_recipients = ['interessent@users.test']
    expected_subject = 'Deine Bestellung (AB-11-B00253) ist eingegangen.'
    expected_body = '''
Hallo Interessent,

vielen Dank für deine Bestellung mit der Nummer AB-11-B00253 am 15.08.2014 über unsere Website.

Folgende Artikel hast du bestellt:

  Beschreibung: Einzelticket, Kategorie Loge
  Anzahl: 5
  Stückpreis: 99,00\xa0€

  Beschreibung: T-Shirt, Größe L
  Anzahl: 2
  Stückpreis: 14,95\xa0€

  Gesamtbetrag: 524,90\xa0€

Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AB-11-B00253

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.acmecon.test/shop/orders

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
    '''.strip()

    assert_email(
        send_email_mock,
        expected_sender,
        expected_recipients,
        expected_subject,
        expected_body,
    )


# helpers


def create_article(
    shop_id: ShopID,
    item_number: str,
    description: str,
    price: Decimal,
    total_quantity: int,
) -> Article:
    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        total_quantity=total_quantity,
    )
