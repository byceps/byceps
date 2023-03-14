"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.article import article_service


@pytest.fixture(scope='module')
def shop(make_brand, make_shop):
    brand = make_brand()
    return make_shop(brand.id)


@pytest.fixture(scope='module')
def article1(shop, make_article):
    return make_article(
        shop.id, item_number='TICKET-2022', description='Ticket for 2022'
    )


@pytest.fixture(scope='module')
def article2(shop, make_article):
    return make_article(
        shop.id, item_number='TICKET-2023', description='Ticket for 2023'
    )


@pytest.fixture(scope='module')
def article3(shop, make_article):
    return make_article(
        shop.id, item_number='SHIRT-2023', description='Shirt for 2023'
    )


@pytest.mark.parametrize(
    'search_term, expected_article_numbers',
    [
        ('2022', {'TICKET-2022'}),
        ('2023', {'TICKET-2023', 'SHIRT-2023'}),
        ('shirt', {'SHIRT-2023'}),
        ('ticket', {'TICKET-2022', 'TICKET-2023'}),
    ],
)
def test_search_multiple_terms(
    admin_app,
    shop,
    article1,
    article2,
    article3,
    search_term,
    expected_article_numbers,
):
    actual = article_service.get_articles_for_shop_paginated(
        shop.id, 1, 10, search_term=search_term
    )

    actual_article_numbers = {article.item_number for article in actual.items}

    assert actual_article_numbers == expected_article_numbers
