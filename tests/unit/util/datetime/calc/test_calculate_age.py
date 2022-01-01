"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date

import pytest

from byceps.util.datetime.calc import calculate_age


SOME_DATE = date(1994, 3, 18)


@pytest.mark.parametrize(
    'today, expected',
    [
        (date(2014, 3, 17), 19),
        (date(2014, 3, 18), 20),
        (date(2014, 3, 19), 20),
        (date(2015, 3, 17), 20),
        (date(2015, 3, 18), 21),
        (date(2015, 3, 19), 21),
    ],
)
def test_calculate_age(today, expected):
    actual = calculate_age(SOME_DATE, today)

    assert actual == expected
