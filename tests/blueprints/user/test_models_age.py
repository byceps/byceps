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


class AgeTestCase(TestCase):

    def setUp(self):
        date_of_birth = date(1994, 3, 18)
        self.user = create_user_with_detail(1, date_of_birth=date_of_birth)

    @params(
        ('2014-03-17', 19),
        ('2014-03-18', 20),
        ('2014-03-19', 20),
        ('2015-03-17', 20),
        ('2015-03-18', 21),
        ('2015-03-19', 21),
    )
    def test_age(self, today_text, expected):
        with freeze_time(today_text):
            self.assertEqual(self.user.detail.age, expected)
