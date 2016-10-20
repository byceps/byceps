# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from nose2.tools import params

from byceps.util.datetime.range import create_adjacent_ranges, DateTimeRange


@params(
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
)
def test_contains(starts_at, ends_at, tested_datetime, expected):
    date_time_range = DateTimeRange(start=starts_at, end=ends_at)

    actual = date_time_range.contains(tested_datetime)

    assert actual == expected


def test_create_adjacent_ranges():
    dt1 = datetime(2014,  8, 15, 12,  0,  0)
    dt2 = datetime(2014,  8, 15, 19, 30,  0)
    dt3 = datetime(2014,  8, 16,  7, 15,  0)
    dt4 = datetime(2014,  8, 18, 22, 45,  0)

    dts = [dt1, dt2, dt3, dt4]

    expected = [
        DateTimeRange(dt1, dt2),
        DateTimeRange(dt2, dt3),
        DateTimeRange(dt3, dt4),
    ]

    actual = create_adjacent_ranges(dts)

    assert list(actual) == expected
