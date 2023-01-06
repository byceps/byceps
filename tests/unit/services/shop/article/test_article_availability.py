"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from freezegun import freeze_time
from moneyed import EUR, Money
import pytest

from byceps.database import generate_uuid
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.article import article_service
from byceps.services.shop.shop.transfer.models import ShopID


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
        assert article_service.is_article_available_now(article) == expected


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
        assert article_service.is_article_available_now(article) == expected


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
        assert article_service.is_article_available_now(article) == expected


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
        assert article_service.is_article_available_now(article) == expected


def create_article(
    available_from: Optional[datetime], available_until: Optional[datetime]
) -> Article:
    return Article(
        id=ArticleID(generate_uuid()),
        shop_id=ShopID('any-shop'),
        item_number=ArticleNumber('article-123'),
        type_=ArticleType.other,
        type_params={},
        description='Cool thing',
        price=Money('1.99', EUR),
        tax_rate=Decimal('0.19'),
        available_from=available_from,
        available_until=available_until,
        total_quantity=1,
        quantity=1,
        max_quantity_per_order=1,
        not_directly_orderable=False,
        separate_order_required=False,
        processing_required=False,
    )
