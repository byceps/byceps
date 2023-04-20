"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

import pytest

from byceps.util.datetime.calc import calculate_days_until


SOME_DATE = date(1994, 3, 18)


@pytest.mark.parametrize(
    ('today', 'expected'),
    [
        (date(2014, 3, 16), 2),
        (date(2014, 3, 17), 1),
        (date(2014, 3, 18), 0),
        (date(2014, 3, 19), 364),
    ],
)
def test_calculate_days_until(today, expected):
    actual = calculate_days_until(SOME_DATE, today)

    assert actual == expected
