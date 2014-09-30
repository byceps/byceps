# -*- coding: utf-8 -*-

from unittest import TestCase

from nose2.tools import params

from byceps.blueprints.shop.models import EuroAmount


class EuroAmountTestCase(TestCase):

    @params(
        (    0, EuroAmount(  0,  0)),
        (    1, EuroAmount(  0,  1)),
        (    5, EuroAmount(  0,  5)),
        (    9, EuroAmount(  0,  9)),
        (   10, EuroAmount(  0, 10)),
        (   99, EuroAmount(  0, 99)),
        (  100, EuroAmount(  1,  0)),
        (  101, EuroAmount(  1,  1)),
        (  111, EuroAmount(  1, 11)),
        (  199, EuroAmount(  1, 99)),
        (  200, EuroAmount(  2,  0)),
        ( 1234, EuroAmount( 12, 34)),
        (12345, EuroAmount(123, 45)),
    )
    def test_from_int(self, value, expected):
        actual = EuroAmount.from_int(value)

        self.assertEquals(actual, expected)

    @params(
        (  -1),
        ( -99),
        (-100),
        (-101),
    )
    def test_from_int_raises_exception_on_negative_value(self, value):
        with self.assertRaises(ValueError):
            EuroAmount.from_int(value)

    @params(
        (EuroAmount(  0,  0),     0),
        (EuroAmount(  0,  1),     1),
        (EuroAmount(  0,  5),     5),
        (EuroAmount(  0,  9),     9),
        (EuroAmount(  0, 10),    10),
        (EuroAmount(  0, 99),    99),
        (EuroAmount(  1,  0),   100),
        (EuroAmount(  1,  1),   101),
        (EuroAmount(  1, 11),   111),
        (EuroAmount(  1, 99),   199),
        (EuroAmount(  2,  0),   200),
        (EuroAmount( 12, 34),  1234),
        (EuroAmount(123, 45), 12345),
    )
    def test_to_int(self, euro_amount, expected):
        actual = euro_amount.to_int()

        self.assertEquals(actual, expected)
