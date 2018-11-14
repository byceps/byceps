"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

from testfixtures.shop_article import create_article
from testfixtures.shop_order import create_order, create_order_item
from testfixtures.user import create_user


def test_without_any_items():
    order = create_order_with_items([])

    assert_decimal_equal(order.total_amount, Decimal('0.00'))


def test_with_single_item():
    order = create_order_with_items([
        (Decimal('49.95'), 1),
    ])

    assert_decimal_equal(order.total_amount, Decimal('49.95'))


def test_with_multiple_items():
    order = create_order_with_items([
        (Decimal('49.95'), 3),
        (Decimal( '6.20'), 1),
        (Decimal('12.53'), 4),
    ])

    assert_decimal_equal(order.total_amount, Decimal('206.17'))


# helpers

def create_order_with_items(price_quantity_pairs):
    user = create_user()

    shop_id = 'shop-123'
    placed_by = user

    order = create_order(shop_id, placed_by)

    for price, quantity in price_quantity_pairs:
        article = create_article(shop_id, price=price, quantity=quantity)
        order_item = create_order_item(order, article, quantity)

    return order.to_transfer_object()


def assert_decimal_equal(actual, expected):
    assert isinstance(actual, Decimal)
    assert actual == expected
