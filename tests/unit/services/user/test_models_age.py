"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

from freezegun import freeze_time
import pytest

from testfixtures.user import create_user_with_detail


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
    user = create_user_with_detail(date_of_birth=date(1994, 3, 18))

    with freeze_time(today_text):
        assert user.detail.age == expected


def test_age_without_date_of_birth():
    user = create_user_with_detail(date_of_birth=None)
    assert user.detail.date_of_birth is None  # precondition

    assert user.detail.age is None
