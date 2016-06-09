# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date
from unittest import TestCase

from nose2.tools import params

from byceps.util.datetime import calculate_age, calculate_days_until


class CalculationTestCase(TestCase):

    def setUp(self):
        self.date = date(1994, 3, 18)

    @params(
        (date(2014, 3, 17), 19),
        (date(2014, 3, 18), 20),
        (date(2014, 3, 19), 20),
        (date(2015, 3, 17), 20),
        (date(2015, 3, 18), 21),
        (date(2015, 3, 19), 21),
    )
    def test_calculate_age(self, today, expected):
        actual = calculate_age(self.date, today)
        self.assertEqual(actual, expected)

    @params(
        (date(2014, 3, 16), 2),
        (date(2014, 3, 17), 1),
        (date(2014, 3, 18), 0),
        (date(2014, 3, 19), 364),
    )
    def test_calculate_days_until(self, today, expected):
        actual = calculate_days_until(self.date, today)
        self.assertEqual(actual, expected)
