"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.util.iterables import index_of


@pytest.mark.parametrize(
    'predicate, iterable, expected',
    [
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
    ],
)
def test_index_of(predicate, iterable, expected):
    actual = index_of(predicate, iterable)
    assert actual == expected
