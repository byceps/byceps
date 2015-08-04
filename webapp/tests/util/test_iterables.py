# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest import TestCase

from nose2.tools import params

from byceps.util.iterables import find, index_of, pairwise


class IterablesTestCase(TestCase):

    @params(
        (
            lambda x: x > 3,
            [],
            None,
        ),
        (
            lambda x: x > 3,
            [-2, 0, 1, 3],
            None,
        ),
        (
            lambda x: x > 3,
            [2, 3, 4, 5],
            4,
        ),
    )
    def test_find(self, predicate, iterable, expected):
        actual = find(predicate, iterable)
        self.assertEqual(actual, expected)

    @params(
        (
            lambda x: x > 3,
            [],
            None,
        ),
        (
            lambda x: x > 1,
            [2, 3, 4, 5],
            0,
        ),
        (
            lambda x: x > 3,
            [2, 3, 4, 5],
            2,
        ),
        (
            lambda x: x > 6,
            [2, 3, 4, 5],
            None,
        ),
    )
    def test_index_of(self, predicate, iterable, expected):
        actual = index_of(predicate, iterable)
        self.assertEqual(actual, expected)

    @params(
        (
            [],
            [],
        ),
        (
            ['a', 'b', 'c'],
            [('a', 'b'), ('b', 'c')],
        ),
        (
            range(5),
            [(0, 1), (1, 2), (2, 3), (3, 4)],
        ),
    )
    def test_pairwise(self, iterable, expected):
        actual = pairwise(iterable)
        self.assertEqual(list(actual), expected)
