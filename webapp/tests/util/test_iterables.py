# -*- coding: utf-8 -*-

from unittest import TestCase

from nose2.tools import params

from byceps.util.iterables import find


class IterablesTestCase(TestCase):

    @params(
        (
            [],
            lambda x: x > 3,
            None,
        ),
        (
            [-2, 0, 1, 3],
            lambda x: x > 3,
            None,
        ),
        (
            [2, 3, 4, 5],
            lambda x: x > 3,
            4,
        ),
    )
    def test_find(self, iterable, predicate, expected):
        actual = find(iterable, predicate)
        self.assertEqual(actual, expected)
