# -*- coding: utf-8 -*-

from datetime import date
from unittest import TestCase

from nose2.tools import params

from byceps.util.datetime import calculate_age, calculate_days_until, MonthDay


class MonthDayTestCase(TestCase):

    @params(
        (date(1994,  3, 18),  3, 18),
        (date(2012,  9, 27),  9, 27),
        (date(2015,  1,  1),  1,  1),
        (date(2022, 12, 31), 12, 31),
    )
    def test_of(self, date, expected_month, expected_day):
        month_day = MonthDay.of(date)

        self.assertEquals(month_day.month, expected_month)
        self.assertEquals(month_day.day, expected_day)

    @params(
        ( 3, 17, date(2005,  2, 17), False),
        ( 3, 17, date(2005,  3, 16), False),
        ( 3, 17, date(2005,  3, 17), True ),
        ( 3, 17, date(2014,  3, 17), True ),
        ( 3, 17, date(2017,  3, 17), True ),
        ( 3, 17, date(2005,  3, 18), False),
        ( 3, 17, date(2005,  4, 17), False),
        (12, 31, date(2010, 12, 30), False),
        (12, 31, date(2010, 12, 31), True ),
    )
    def test_matches(self, month, day, date, expected):
        month_day = MonthDay(month=month, day=day)
        actual = month_day.matches(date)

        self.assertEquals(actual, expected)


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
        self.assertEquals(actual, expected)

    @params(
        (date(2014, 3, 16), 2),
        (date(2014, 3, 17), 1),
        (date(2014, 3, 18), 0),
        (date(2014, 3, 19), 364),
    )
    def test_calculate_days_until(self, today, expected):
        actual = calculate_days_until(self.date, today)
        self.assertEquals(actual, expected)
