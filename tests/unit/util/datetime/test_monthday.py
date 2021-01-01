"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

import pytest

from byceps.util.datetime.monthday import MonthDay


@pytest.mark.parametrize(
    'date, expected_month, expected_day',
    [
        (date(1994,  3, 18),  3, 18),
        (date(2012,  9, 27),  9, 27),
        (date(2015,  1,  1),  1,  1),
        (date(2022, 12, 31), 12, 31),
    ],
)
def test_of(date, expected_month, expected_day):
    month_day = MonthDay.of(date)

    assert month_day.month == expected_month
    assert month_day.day == expected_day


@pytest.mark.parametrize(
    'month, day, date, expected',
    [
        ( 3, 17, date(2005,  2, 17), False),
        ( 3, 17, date(2005,  3, 16), False),
        ( 3, 17, date(2005,  3, 17), True ),
        ( 3, 17, date(2014,  3, 17), True ),
        ( 3, 17, date(2017,  3, 17), True ),
        ( 3, 17, date(2005,  3, 18), False),
        ( 3, 17, date(2005,  4, 17), False),
        (12, 31, date(2010, 12, 30), False),
        (12, 31, date(2010, 12, 31), True ),
    ],
)
def test_matches(month, day, date, expected):
    month_day = MonthDay(month=month, day=day)

    actual = month_day.matches(date)

    assert actual == expected
