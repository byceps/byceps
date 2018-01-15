"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from testfixtures.shop_article import create_article


@pytest.mark.parametrize('now, expected', [
    (datetime(2014,  4,  8, 12,  0,  0), False),
    (datetime(2014,  9, 15, 17, 59, 59), False),
    (datetime(2014,  9, 15, 18,  0,  0), True ),
    (datetime(2014,  9, 19, 15,  0,  0), True ),
    (datetime(2014,  9, 23, 17, 59, 59), True ),
    (datetime(2014,  9, 23, 18,  0,  0), False),
    (datetime(2014, 11,  4, 12,  0,  0), False),
])
def test_is_available_with_start_and_end(now, expected):
    article = create_article(
        available_from=datetime(2014, 9, 15, 18, 0, 0),
        available_until=datetime(2014, 9, 23, 18, 0, 0))

    with freeze_time(now):
        assert article.is_available == expected


@pytest.mark.parametrize('now, expected', [
    (datetime(2014,  4,  8, 12,  0,  0), False),
    (datetime(2014,  9, 15, 17, 59, 59), False),
    (datetime(2014,  9, 15, 18,  0,  0), True ),
    (datetime(2014,  9, 19, 15,  0,  0), True ),
    (datetime(2014,  9, 23, 17, 59, 59), True ),
    (datetime(2014,  9, 23, 18,  0,  0), True ),
    (datetime(2014, 11,  4, 12,  0,  0), True ),
])
def test_is_available_with_start_and_without_end(now, expected):
    article = create_article(
        available_from=datetime(2014, 9, 15, 18, 0, 0),
        available_until=None)

    with freeze_time(now):
        assert article.is_available == expected


@pytest.mark.parametrize('now, expected', [
    (datetime(2014,  4,  8, 12,  0,  0), True ),
    (datetime(2014,  9, 15, 17, 59, 59), True ),
    (datetime(2014,  9, 15, 18,  0,  0), True ),
    (datetime(2014,  9, 19, 15,  0,  0), True ),
    (datetime(2014,  9, 23, 17, 59, 59), True ),
    (datetime(2014,  9, 23, 18,  0,  0), False),
    (datetime(2014, 11,  4, 12,  0,  0), False),
])
def test_is_available_without_start_and_with_end(now, expected):
    article = create_article(
        available_from=None,
        available_until=datetime(2014, 9, 23, 18, 0, 0))

    with freeze_time(now):
        assert article.is_available == expected


@pytest.mark.parametrize('now, expected', [
    (datetime(2014,  4,  8, 12,  0,  0), True ),
    (datetime(2014,  9, 15, 17, 59, 59), True ),
    (datetime(2014,  9, 15, 18,  0,  0), True ),
    (datetime(2014,  9, 19, 15,  0,  0), True ),
    (datetime(2014,  9, 23, 17, 59, 59), True ),
    (datetime(2014,  9, 23, 18,  0,  0), True ),
    (datetime(2014, 11,  4, 12,  0,  0), True ),
])
def test_is_available_without_start_and_without_end(now, expected):
    article = create_article(
        available_from=None,
        available_until=None)

    with freeze_time(now):
        assert article.is_available == expected
