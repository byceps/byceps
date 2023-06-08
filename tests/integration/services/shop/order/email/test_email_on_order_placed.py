"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
from moneyed import EUR, Money
import pytest

from byceps.services.brand.models import Brand
from byceps.services.email.models import NameAndAddress
from byceps.services.shop.article.models import Article, ArticleNumber
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.email.order_email_service import OrderEmailData
from byceps.services.shop.order.models.order import Order, Orderer
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.user.models.user import User

from tests.helpers import current_user_set

from .helpers import get_current_user_for_user, place_order_with_items


@pytest.fixture(scope='module')
def customer(make_user) -> User:
    return make_user('Interessent', email_address='interessent@users.test')


@pytest.fixture()
def orderer(make_orderer, customer: User) -> Orderer:
    return make_orderer(customer.id)


@pytest.fixture()
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='AB-11-B', value=252
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture()
def article1(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('AB-11-A00003'),
        description='Einzelticket, Kategorie Loge',
        price=Money('99.00', EUR),
    )


@pytest.fixture()
def article2(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('AB-11-A00007'),
        description='T-Shirt, Größe L',
        price=Money('14.95', EUR),
    )


@pytest.fixture()
def order(
    storefront: Storefront,
    article1: Article,
    article2: Article,
    orderer: Orderer,
    email_payment_instructions_snippets,
    email_footer_snippets,
):
    created_at = datetime(2014, 8, 15, 20, 7, 43)

    items_with_quantity = [
        (article1, 5),
        (article2, 2),
    ]

    return place_order_with_items(
        storefront.id, orderer, created_at, items_with_quantity
    )


def test_email_on_order_placed(
    site_app: Flask,
    customer: User,
    shop_brand: Brand,
    order: Order,
):
    app = site_app

    language_code = 'de'
    order_email_data = OrderEmailData(
        sender=NameAndAddress(name=None, address='noreply@acmecon.test'),
        order=order,
        brand_id=shop_brand.id,
        orderer=customer,
        orderer_email_address='interessent@users.test',
    )
    current_user = get_current_user_for_user(customer, language_code)

    with current_user_set(app, current_user), app.app_context():
        actual = (
            order_email_service.assemble_email_for_incoming_order_to_orderer(
                order_email_data, language_code
            )
        )

    assert actual.sender == NameAndAddress(
        name=None, address='noreply@acmecon.test'
    )
    assert actual.recipients == ['interessent@users.test']
    assert actual.subject == 'Deine Bestellung (AB-11-B00253) ist eingegangen.'
    assert (
        actual.body
        == '''
Hallo Interessent,

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

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der {brand_title}

--\x20
{brand_title}

E-Mail: info@acmecon.test
    '''.strip().format(
            brand_title=shop_brand.title
        )
    )
