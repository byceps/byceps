"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

from freezegun import freeze_time
import pytest

from byceps.services.orga.transfer.models import Birthday


@pytest.mark.parametrize(
    'today_text, expected',
    [
        ('2014-03-17', 19),
        ('2014-03-18', 20),
        ('2014-03-19', 20),
        ('2015-03-17', 20),
        ('2015-03-18', 21),
        ('2015-03-19', 21),
    ],
)
def test_age(today_text, expected):
    birthday = Birthday(date(1994, 3, 18))

    with freeze_time(today_text):
        assert birthday.age == expected


@pytest.mark.parametrize(
    'today_text, expected',
    [
        ('2014-03-16',   2),
        ('2014-03-17',   1),
        ('2014-03-18',   0),
        ('2014-03-19', 364),
    ],
)
def test_days_until_next_birthday(today_text, expected):
    birthday = Birthday(date(1994, 3, 18))

    with freeze_time(today_text):
        assert birthday.days_until_next_birthday == expected


@pytest.mark.parametrize(
    'today_text, expected',
    [
        ('1994-03-17', False),
        ('1994-03-18', True ),
        ('1994-03-19', False),
        ('2014-03-17', False),
        ('2014-03-18', True ),
        ('2014-03-19', False),
    ],
)
def test_is_today(today_text, expected):
    birthday = Birthday(date(1994, 3, 18))

    with freeze_time(today_text):
        assert birthday.is_today == expected
