"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.util.datetime.range import DateTimeRange


@pytest.mark.parametrize(
    ('starts_at', 'ends_at', 'tested_datetime', 'expected'),
    [
        (
            datetime(2014,  8, 15, 12,  0,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            datetime(2014,  8, 15, 11, 59, 59),
            False,
        ),
        (
            datetime(2014,  8, 15, 12,  0,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            datetime(2014,  8, 15, 12,  0,  0),
            True,
        ),
        (
            datetime(2014,  8, 15, 12,  0,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            datetime(2014,  8, 15, 12,  0,  1),
            True,
        ),
        (
            datetime(2014,  8, 15, 12,  0,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            datetime(2014,  8, 15, 17, 48, 23),
            True,
        ),
        (
            datetime(2014,  8, 15, 12,  0,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            datetime(2014,  8, 15, 19, 29, 59),
            True,
        ),
        (
            datetime(2014,  8, 15, 12,  0,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            False,
        ),
        (
            datetime(2014,  8, 15, 12,  0,  0),
            datetime(2014,  8, 15, 19, 30,  0),
            datetime(2014,  8, 15, 19, 30,  1),
            False,
        ),
    ],
)
def test_contains(starts_at, ends_at, tested_datetime, expected):
    date_time_range = DateTimeRange(start=starts_at, end=ends_at)

    actual = date_time_range.contains(tested_datetime)

    assert actual == expected
