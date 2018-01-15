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

    actual = order.calculate_total_price()

    assert_decimal_equal(actual, Decimal('0.00'))


def test_with_single_item():
    order = create_order_with_items([
        (Decimal('49.95'), 1),
    ])

    actual = order.calculate_total_price()

    assert_decimal_equal(actual, Decimal('49.95'))


def test_with_multiple_items():
    order = create_order_with_items([
        (Decimal('49.95'), 3),
        (Decimal( '6.20'), 1),
        (Decimal('12.53'), 4),
    ])

    actual = order.calculate_total_price()

    assert_decimal_equal(actual, Decimal('206.17'))


# helpers

def create_order_with_items(price_quantity_pairs):
    user = create_user()

    party_id = 'acme-party-2016'
    placed_by = user

    order = create_order(party_id, placed_by)

    for price, quantity in price_quantity_pairs:
        article = create_article(price=price, quantity=quantity)
        order_item = create_order_item(order, article, quantity)

    return order


def assert_decimal_equal(actual, expected):
    assert isinstance(actual, Decimal)
    assert actual == expected
