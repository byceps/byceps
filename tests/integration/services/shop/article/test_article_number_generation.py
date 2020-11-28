"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.article import (
    sequence_service as article_sequence_service,
)
from byceps.services.shop.shop import service as shop_service

from tests.integration.services.shop.helpers import create_shop


@pytest.fixture(scope='module')
def shop1(brand):
    shop = create_shop(brand.id)
    yield shop
    shop_service.delete_shop(shop.id)


@pytest.fixture(scope='module')
def shop2(brand):
    shop = create_shop(brand.id)
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
