"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.article import (
    sequence_service as article_sequence_service,
)
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
)
from byceps.services.shop.shop import service as shop_service


@pytest.fixture(scope='module')
def shop1(email_config):
    shop = shop_service.create_shop('shop-01', 'Some Shop', email_config.id)
    yield shop
    shop_service.delete_shop(shop.id)


@pytest.fixture(scope='module')
def shop2(email_config):
    shop = shop_service.create_shop('shop-02', 'Another Shop', email_config.id)
    yield shop
    shop_service.delete_shop(shop.id)


def test_generate_article_number_default(admin_app, shop1):
    shop = shop1

    article_number_sequence_id = (
        article_sequence_service.create_article_number_sequence(
            shop.id, 'AEC-01-A'
        )
    )

    actual = article_sequence_service.generate_article_number(
        article_number_sequence_id
    )

    assert actual == 'AEC-01-A00001'

    article_sequence_service.delete_article_number_sequence(
        article_number_sequence_id
    )


def test_generate_article_number_custom(admin_app, shop2):
    shop = shop2

    article_number_sequence_id = (
        article_sequence_service.create_article_number_sequence(
            shop.id,
            'XYZ-09-A',
            value=41,
        )
    )

    actual = article_sequence_service.generate_article_number(
        article_number_sequence_id
    )

    assert actual == 'XYZ-09-A00042'

    article_sequence_service.delete_article_number_sequence(
        article_number_sequence_id
    )


def test_generate_order_number_default(admin_app, shop1):
    shop = shop1

    order_number_sequence_id = (
        order_sequence_service.create_order_number_sequence(shop.id, 'AEC-01-B')
    )

    actual = order_sequence_service.generate_order_number(
        order_number_sequence_id
    )

    assert actual == 'AEC-01-B00001'

    order_sequence_service.delete_order_number_sequence(
        order_number_sequence_id
    )


def test_generate_order_number_custom(admin_app, shop2):
    shop = shop2

    last_assigned_order_sequence_number = 206

    order_number_sequence_id = (
        order_sequence_service.create_order_number_sequence(
            shop.id, 'LOL-03-B', value=last_assigned_order_sequence_number
        )
    )

    actual = order_sequence_service.generate_order_number(
        order_number_sequence_id
    )

    assert actual == 'LOL-03-B00207'

    order_sequence_service.delete_order_number_sequence(
        order_number_sequence_id
    )
