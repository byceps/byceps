"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time
import pytest

from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.article.service import is_article_available_now


@pytest.mark.parametrize(
    'now, expected',
    [
        (datetime(2014,  4,  8, 12,  0,  0), False),
        (datetime(2014,  9, 15, 17, 59, 59), False),
        (datetime(2014,  9, 15, 18,  0,  0), True ),
        (datetime(2014,  9, 19, 15,  0,  0), True ),
        (datetime(2014,  9, 23, 17, 59, 59), True ),
        (datetime(2014,  9, 23, 18,  0,  0), False),
        (datetime(2014, 11,  4, 12,  0,  0), False),
    ],
)
def test_is_available_with_start_and_end(now, expected):
    article = create_article(
        datetime(2014, 9, 15, 18, 0, 0),
        datetime(2014, 9, 23, 18, 0, 0),
    )

    with freeze_time(now):
        assert is_article_available_now(article) == expected


@pytest.mark.parametrize(
    'now, expected',
    [
        (datetime(2014,  4,  8, 12,  0,  0), False),
        (datetime(2014,  9, 15, 17, 59, 59), False),
        (datetime(2014,  9, 15, 18,  0,  0), True ),
        (datetime(2014,  9, 19, 15,  0,  0), True ),
        (datetime(2014,  9, 23, 17, 59, 59), True ),
        (datetime(2014,  9, 23, 18,  0,  0), True ),
        (datetime(2014, 11,  4, 12,  0,  0), True ),
    ],
)
def test_is_available_with_start_and_without_end(now, expected):
    article = create_article(
        datetime(2014, 9, 15, 18, 0, 0),
        None,
    )

    with freeze_time(now):
        assert is_article_available_now(article) == expected


@pytest.mark.parametrize(
    'now, expected',
    [
        (datetime(2014,  4,  8, 12,  0,  0), True ),
        (datetime(2014,  9, 15, 17, 59, 59), True ),
        (datetime(2014,  9, 15, 18,  0,  0), True ),
        (datetime(2014,  9, 19, 15,  0,  0), True ),
        (datetime(2014,  9, 23, 17, 59, 59), True ),
        (datetime(2014,  9, 23, 18,  0,  0), False),
        (datetime(2014, 11,  4, 12,  0,  0), False),
    ],
)
def test_is_available_without_start_and_with_end(now, expected):
    article = create_article(
        None,
        datetime(2014, 9, 23, 18, 0, 0),
    )

    with freeze_time(now):
        assert is_article_available_now(article) == expected


@pytest.mark.parametrize(
    'now, expected',
    [
        (datetime(2014,  4,  8, 12,  0,  0), True ),
        (datetime(2014,  9, 15, 17, 59, 59), True ),
        (datetime(2014,  9, 15, 18,  0,  0), True ),
        (datetime(2014,  9, 19, 15,  0,  0), True ),
        (datetime(2014,  9, 23, 17, 59, 59), True ),
        (datetime(2014,  9, 23, 18,  0,  0), True ),
        (datetime(2014, 11,  4, 12,  0,  0), True ),
    ],
)
def test_is_available_without_start_and_without_end(now, expected):
    article = create_article(
        None,
        None,
    )

    with freeze_time(now):
        assert is_article_available_now(article) == expected


def create_article(available_from, available_until):
    return Article(
        id='00000000-0000-0000-0000-000000000001',
        shop_id='any-shop',
        item_number='article-123',
        description='Cool thing',
        price=Decimal('1.99'),
        tax_rate=Decimal('0.19'),
        available_from=available_from,
        available_until=available_until,
        total_quantity=1,
        quantity=1,
        max_quantity_per_order=1,
        not_directly_orderable=False,
        requires_separate_order=False,
        shipping_required=False,
    )
