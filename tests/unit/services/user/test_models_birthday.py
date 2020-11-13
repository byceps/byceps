"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

from freezegun import freeze_time
import pytest

from testfixtures.user import create_user, create_user_with_detail


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
    user = create_user_with_detail(date_of_birth=date(1994, 3, 18))

    with freeze_time(today_text):
        assert user.detail.days_until_next_birthday == expected


def test_days_until_next_birthday_without_date_of_birth():
    user = _create_user_without_date_of_birth()

    assert user.detail.days_until_next_birthday is None


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
def test_is_birthday_today(today_text, expected):
    user = create_user_with_detail(date_of_birth=date(1994, 3, 18))

    with freeze_time(today_text):
        assert user.detail.is_birthday_today == expected


def test_is_birthday_today_without_date_of_birth():
    user = _create_user_without_date_of_birth()

    assert user.detail.is_birthday_today is None


def _create_user_without_date_of_birth():
    user = create_user()
    assert user.detail.date_of_birth is None  # precondition
    return user
