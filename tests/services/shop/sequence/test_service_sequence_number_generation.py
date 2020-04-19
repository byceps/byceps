"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.sequence import service as sequence_service
from byceps.services.shop.shop import service as shop_service

from ....conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


@pytest.fixture(scope='module')
def email_config(make_email_config):
    return make_email_config()


@pytest.fixture(scope='module')
def shop1(email_config):
    return shop_service.create_shop('shop-01', 'Some Shop', email_config.id)


@pytest.fixture(scope='module')
def shop2(email_config):
    return shop_service.create_shop('shop-02', 'Another Shop', email_config.id)


def test_generate_article_number_default(app, shop1):
    shop = shop1

    sequence_service.create_article_number_sequence(shop.id, 'AEC-01-A')

    actual = sequence_service.generate_article_number(shop.id)

    assert actual == 'AEC-01-A00001'

    sequence_service.delete_article_number_sequence(shop.id)
    sequence_service.delete_order_number_sequence(shop.id)


def test_generate_article_number_custom(app, shop2):
    shop = shop2

    sequence_service.create_article_number_sequence(
        shop.id,
        'XYZ-09-A',
        value=41,
    )

    actual = sequence_service.generate_article_number(shop.id)

    assert actual == 'XYZ-09-A00042'

    sequence_service.delete_article_number_sequence(shop.id)
    sequence_service.delete_order_number_sequence(shop.id)


def test_generate_order_number_default(app, shop1):
    shop = shop1

    sequence_service.create_order_number_sequence(shop.id, 'AEC-01-B')

    actual = sequence_service.generate_order_number(shop.id)

    assert actual == 'AEC-01-B00001'

    sequence_service.delete_article_number_sequence(shop.id)
    sequence_service.delete_order_number_sequence(shop.id)


def test_generate_order_number_custom(app, shop2):
    shop = shop2

    last_assigned_order_sequence_number = 206

    sequence_service.create_order_number_sequence(
        shop.id, 'LOL-03-B', value=last_assigned_order_sequence_number
    )

    actual = sequence_service.generate_order_number(shop.id)

    assert actual == 'LOL-03-B00207'

    sequence_service.delete_article_number_sequence(shop.id)
    sequence_service.delete_order_number_sequence(shop.id)
