# -*- coding: utf-8 -*-

from unittest import TestCase

from nose2.tools import params

from byceps.util.iterables import find, index_of, pairwise


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

    @params(
        (
            [],
            lambda x: x > 3,
            None,
        ),
        (
            [2, 3, 4, 5],
            lambda x: x > 1,
            0,
        ),
        (
            [2, 3, 4, 5],
            lambda x: x > 3,
            2,
        ),
        (
            [2, 3, 4, 5],
            lambda x: x > 6,
            None,
        ),
    )
    def test_index_of(self, iterable, predicate, expected):
        actual = index_of(iterable, predicate)
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
