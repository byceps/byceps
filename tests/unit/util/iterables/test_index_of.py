"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.iterables import index_of


@pytest.mark.parametrize(
    'iterable, predicate, expected',
    [
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
    ],
)
def test_index_of(iterable, predicate, expected):
    actual = index_of(iterable, predicate)
    assert actual == expected
