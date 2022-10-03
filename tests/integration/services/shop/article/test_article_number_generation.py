"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.article import article_sequence_service


@pytest.fixture(scope='module')
def shop1(make_brand, make_shop):
    brand = make_brand()

    return make_shop(brand.id)


@pytest.fixture(scope='module')
def shop2(make_brand, make_shop):
    brand = make_brand()

    return make_shop(brand.id)


def test_generate_article_number_default(admin_app, shop1):
    shop = shop1

    sequence = article_sequence_service.create_article_number_sequence(
        shop.id, 'ONE-01-A'
    )

    actual = article_sequence_service.generate_article_number(sequence.id)

    assert actual == 'ONE-01-A00001'


def test_generate_article_number_custom(admin_app, shop2):
    shop = shop2

    sequence = article_sequence_service.create_article_number_sequence(
        shop.id, 'TWO-02-A', value=41
    )

    actual = article_sequence_service.generate_article_number(sequence.id)

    assert actual == 'TWO-02-A00042'
