# -*- coding: utf-8 -*-

from datetime import date
from unittest import TestCase

from freezegun import freeze_time
from nose2.tools import params

from byceps.blueprints.user.models import UserDetail


class AgeTestCase(TestCase):

    def setUp(self):
        date_of_birth = date(1994, 3, 18)
        self.user_detail = UserDetail(date_of_birth=date_of_birth)

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
            self.assertEquals(self.user_detail.age, expected)
