# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest import TestCase

from nose2.tools import params

from byceps.util.datetime import DateTimeRange


class DateTimeRangeTestCase(TestCase):

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
    def test_contains(self, starts_at, ends_at, tested_datetime, expected):
        date_time_range = DateTimeRange(start=starts_at, end=ends_at)

        actual = date_time_range.contains(tested_datetime)

        self.assertEqual(actual, expected)
