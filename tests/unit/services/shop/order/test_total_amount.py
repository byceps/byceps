"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from datetime import datetime

from moneyed import EUR, Money
import pytest

from byceps.services.shop.article.models import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_domain_service
from byceps.services.shop.order.models.checkout import IncomingOrder
from byceps.services.shop.order.models.order import Orderer
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID

from tests.helpers import generate_token


SHOP_ID = ShopID(generate_token())
STOREFRONT_ID = StorefrontID(generate_token())


@pytest.fixture(scope='module')
def article1(make_article) -> Article:
    return make_article(price=Money('49.95', EUR))


@pytest.fixture(scope='module')
def article2(make_article) -> Article:
    return make_article(price=Money('6.20', EUR))


@pytest.fixture(scope='module')
def article3(make_article) -> Article:
    return make_article(price=Money('12.53', EUR))


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


def build_incoming_order(
    orderer: Orderer, articles: Iterable[tuple[Article, int]]
) -> IncomingOrder:
    cart = Cart(EUR)
    for article, quantity in articles:
        cart.add_item(article, quantity)

    return order_domain_service.place_order(
        datetime.utcnow(),
        SHOP_ID,
        STOREFRONT_ID,
        orderer,
        EUR,
        cart,
    )
