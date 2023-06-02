"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal

from moneyed import EUR, Money
import pytest

from byceps.services.shop.article.models import (
    Article,
    ArticleID,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service
from byceps.services.shop.order.models.checkout import IncomingOrder
from byceps.services.shop.order.models.order import Orderer
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.typing import UserID

from tests.helpers import generate_token, generate_uuid


SHOP_ID = ShopID(generate_token())
STOREFRONT_ID = StorefrontID(generate_token())


@pytest.fixture(scope='module')
def article1() -> Article:
    return build_article(ArticleNumber('LF-01-A00001'), 'Artikel #1', '49.95')


@pytest.fixture(scope='module')
def article2() -> Article:
    return build_article(ArticleNumber('LF-01-A00002'), 'Artikel #2', '6.20')


@pytest.fixture(scope='module')
def article3() -> Article:
    return build_article(ArticleNumber('LF-01-A00003'), 'Artikel #3', '12.53')


@pytest.fixture(scope='module')
def orderer() -> Orderer:
    return Orderer(
        user_id=UserID(generate_uuid()),
        company=None,
        first_name='Pam',
        last_name='Locke',
        country='UK',
        zip_code='LS1 5BZ',
        city='Leeds',
        street='High Street 34a',
    )


def test_without_any_items(orderer: Orderer):
    order = build_incoming_order(orderer, [])

    assert order.total_amount == EUR.zero


def test_with_single_item(orderer: Orderer, article1: Article):
    order = build_incoming_order(
        orderer,
        [
            (article1, 1),
        ],
    )

    assert order.total_amount == Money('49.95', EUR)


def test_with_multiple_items(
    orderer: Orderer,
    article1: Article,
    article2: Article,
    article3: Article,
):
    order = build_incoming_order(
        orderer,
        [
            (article1, 3),
            (article2, 1),
            (article3, 4),
        ],
    )

    assert order.total_amount == Money('206.17', EUR)


# helpers


def build_article(
    article_number_str: str, description: str, price_amount_str: str
) -> Article:
    return Article(
        id=ArticleID(generate_uuid()),
        shop_id=SHOP_ID,
        item_number=ArticleNumber(article_number_str),
        type_=ArticleType.physical,
        type_params={},
        description=description,
        price=Money(price_amount_str, EUR),
        tax_rate=Decimal('0.19'),
        available_from=None,
        available_until=None,
        total_quantity=999,
        quantity=999,
        max_quantity_per_order=99,
        not_directly_orderable=False,
        separate_order_required=False,
        processing_required=False,
    )


def build_incoming_order(
    orderer: Orderer, articles: Iterable[tuple[Article, int]]
) -> IncomingOrder:
    cart = Cart(EUR)
    for article, quantity in articles:
        cart.add_item(article, quantity)

    return order_checkout_service.build_incoming_order(
        datetime.utcnow(),
        SHOP_ID,
        STOREFRONT_ID,
        orderer,
        EUR,
        cart,
    )
