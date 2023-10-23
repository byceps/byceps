"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.shop.article import article_domain_service


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), False),
        (datetime(2014, 9, 15, 17, 59, 59), False),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), False),
        (datetime(2014, 11, 4, 12, 0, 0), False),
    ],
)
def test_is_available_with_start_and_end(make_article, now, expected):
    article = make_article(
        available_from=datetime(2014, 9, 15, 18, 0, 0),
        available_until=datetime(2014, 9, 23, 18, 0, 0),
    )

    with freeze_time(now):
        assert (
            article_domain_service.is_article_available_now(article) == expected
        )


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), False),
        (datetime(2014, 9, 15, 17, 59, 59), False),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), True),
        (datetime(2014, 11, 4, 12, 0, 0), True),
    ],
)
def test_is_available_with_start_and_without_end(make_article, now, expected):
    article = make_article(
        available_from=datetime(2014, 9, 15, 18, 0, 0),
    )

    with freeze_time(now):
        assert (
            article_domain_service.is_article_available_now(article) == expected
        )


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), True),
        (datetime(2014, 9, 15, 17, 59, 59), True),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), False),
        (datetime(2014, 11, 4, 12, 0, 0), False),
    ],
)
def test_is_available_without_start_and_with_end(make_article, now, expected):
    article = make_article(
        available_until=datetime(2014, 9, 23, 18, 0, 0),
    )

    with freeze_time(now):
        assert (
            article_domain_service.is_article_available_now(article) == expected
        )


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), True),
        (datetime(2014, 9, 15, 17, 59, 59), True),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), True),
        (datetime(2014, 11, 4, 12, 0, 0), True),
    ],
)
def test_is_available_without_start_and_without_end(
    make_article, now, expected
):
    article = make_article()

    with freeze_time(now):
        assert (
            article_domain_service.is_article_available_now(article) == expected
        )
