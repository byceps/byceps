"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from freezegun import freeze_time
from nose2.tools import params

from testfixtures.user import create_user_with_detail


@params(
    ('2014-03-16',   2),
    ('2014-03-17',   1),
    ('2014-03-18',   0),
    ('2014-03-19', 364),
)
def test_days_until_next_birthday(today_text, expected):
    user = create_user_with_detail(date_of_birth=date(1994, 3, 18))

    with freeze_time(today_text):
        assert user.detail.days_until_next_birthday == expected


@params(
    ('1994-03-17', False),
    ('1994-03-18', True ),
    ('1994-03-19', False),
    ('2014-03-17', False),
    ('2014-03-18', True ),
    ('2014-03-19', False),
)
def test_is_birthday_today(today_text, expected):
    user = create_user_with_detail(date_of_birth=date(1994, 3, 18))

    with freeze_time(today_text):
        assert user.detail.is_birthday_today == expected
