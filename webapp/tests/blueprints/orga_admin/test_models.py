# -*- coding: utf-8 -*-

from datetime import date
from functools import partial
from unittest import TestCase

from nose2.tools import params

from byceps.blueprints.user.models import User
from byceps.blueprints.orga_admin.models import Birthday, MonthDay, \
    sort_birthdays


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


class BirthdayTestCase(TestCase):

    def setUp(self):
        self.date_of_birth = date(1994, 3, 18)

    @params(
        (date(2014, 3, 17), 19),
        (date(2014, 3, 18), 20),
        (date(2014, 3, 19), 20),
        (date(2015, 3, 17), 20),
        (date(2015, 3, 18), 21),
        (date(2015, 3, 19), 21),
    )
    def test_age(self, today, expected):
        birthday = create_birthday(self.date_of_birth, today)

        self.assertEquals(birthday.age, expected)

    @params(
        (date(2014, 3, 16), 2),
        (date(2014, 3, 17), 1),
        (date(2014, 3, 18), 0),
        (date(2014, 3, 19), 364),
    )
    def test_days_until(self, today, expected):
        birthday = create_birthday(self.date_of_birth, today)

        self.assertEquals(birthday.days_until, expected)

    @params(
        (date(1994, 3, 17), False),
        (date(1994, 3, 18), True),
        (date(1994, 3, 19), False),
        (date(2014, 3, 17), False),
        (date(2014, 3, 18), True),
        (date(2014, 3, 19), False),
    )
    def test_is_today(self, today, expected):
        birthday = create_birthday(self.date_of_birth, today)

        self.assertEquals(birthday.is_today, expected)


class BirthdayListTestCase(TestCase):

    def test_sort(self):
        today = date(1994, 9, 30)

        to_birthday = partial(create_birthday, today=today)

        def to_birthdays(dates_of_birth):
            return map(to_birthday, dates_of_birth)

        birthdays = to_birthdays(set([
            date(1985,  9, 29),
            date(1987, 10,  1),
            date(1991, 11, 14),
            date(1992, 11, 14),
            date(1994,  9, 30),
        ]))

        expected = list(to_birthdays([
            date(1994,  9, 30),
            date(1987, 10,  1),
            date(1991, 11, 14),
            date(1992, 11, 14),
            date(1985,  9, 29),
        ]))

        actual = list(sort_birthdays(birthdays))
        self.assertEquals(actual, expected)


def create_birthday(date_of_birth, today):
    return Birthday.of(None, date_of_birth, today)
