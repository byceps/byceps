"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from datetime import datetime

from moneyed import EUR, Money
import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_domain_service
from byceps.services.shop.order.errors import CartEmptyError
from byceps.services.shop.order.log.models import OrderLogEntry
from byceps.services.shop.order.models.checkout import IncomingOrder
from byceps.services.shop.order.models.order import Orderer
from byceps.services.shop.product.models import Product
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.util.result import Err, Result

from tests.helpers import generate_token


SHOP_ID = ShopID(generate_token())
STOREFRONT_ID = StorefrontID(generate_token())


@pytest.fixture(scope='module')
def product1(make_product) -> Product:
    return make_product(price=Money('49.95', EUR))


@pytest.fixture(scope='module')
def product2(make_product) -> Product:
    return make_product(price=Money('6.20', EUR))


@pytest.fixture(scope='module')
def product3(make_product) -> Product:
    return make_product(price=Money('12.53', EUR))


def test_without_any_items(orderer: Orderer):
    empty_cart = Cart(EUR)

    result = place_order(orderer, empty_cart)

    assert result == Err(CartEmptyError())


def test_with_single_item(orderer: Orderer, product1: Product):
    order = build_incoming_order(
        orderer,
        [
            (product1, 1),
        ],
    )

    assert order.total_amount == Money('49.95', EUR)


def test_with_multiple_items(
    orderer: Orderer,
    product1: Product,
    product2: Product,
    product3: Product,
):
    order = build_incoming_order(
        orderer,
        [
            (product1, 3),
            (product2, 1),
            (product3, 4),
        ],
    )

    assert order.total_amount == Money('206.17', EUR)


# helpers


def build_incoming_order(
    orderer: Orderer, products: Iterable[tuple[Product, int]]
) -> IncomingOrder:
    cart = Cart(EUR)
    for product, quantity in products:
        cart.add_item(product, quantity)

    incoming_order, _ = place_order(orderer, cart).unwrap()

    return incoming_order


def place_order(
    orderer: Orderer, cart: Cart
) -> Result[tuple[IncomingOrder, OrderLogEntry], CartEmptyError]:
    return order_domain_service.place_order(
        datetime.utcnow(), SHOP_ID, STOREFRONT_ID, orderer, cart
    )
