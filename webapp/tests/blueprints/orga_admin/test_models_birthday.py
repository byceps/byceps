# -*- coding: utf-8 -*-

from datetime import date
from functools import partial
from unittest import TestCase

from freezegun import freeze_time
from nose2.tools import params

from byceps.blueprints.orga_admin.models import Birthday, sort_birthdays

from testfixtures.user import create_user_with_detail


class BirthdayListTestCase(TestCase):

    @freeze_time('1994-09-30')
    def test_sort(self):
        birthday1985 = create_birthday(date(1985,  9, 29))
        birthday1987 = create_birthday(date(1987, 10,  1))
        birthday1991 = create_birthday(date(1991, 11, 14))
        birthday1992 = create_birthday(date(1992, 11, 14))
        birthday1994 = create_birthday(date(1994,  9, 30))

        birthdays = [
            birthday1994,
            birthday1992,
            birthday1985,
            birthday1991,
            birthday1987,
        ]

        expected = [
            birthday1994,
            birthday1987,
            birthday1991,
            birthday1992,
            birthday1985,
        ]

        actual = list(sort_birthdays(birthdays))
        self.assertEquals(actual, expected)


def create_birthday(date_of_birth):
    user = create_user_with_detail(42, date_of_birth=date_of_birth)
    return Birthday.of(user)
