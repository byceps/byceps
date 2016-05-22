# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date
from unittest import TestCase

from freezegun import freeze_time
from nose2.tools import params

from testfixtures.user import create_user_with_detail


class BirthdayTestCase(TestCase):

    def setUp(self):
        date_of_birth = date(1994, 3, 18)
        self.user = create_user_with_detail(1, date_of_birth=date_of_birth)

    @params(
        ('2014-03-16',   2),
        ('2014-03-17',   1),
        ('2014-03-18',   0),
        ('2014-03-19', 364),
    )
    def test_days_until_next_birthday(self, today_text, expected):
        with freeze_time(today_text):
            actual = self.user.detail.days_until_next_birthday
            self.assertEqual(actual, expected)

    @params(
        ('1994-03-17', False),
        ('1994-03-18', True ),
        ('1994-03-19', False),
        ('2014-03-17', False),
        ('2014-03-18', True ),
        ('2014-03-19', False),
    )
    def test_is_birthday_today(self, today_text, expected):
        with freeze_time(today_text):
            self.assertEqual(self.user.detail.is_birthday_today, expected)
