"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.iterables import pairwise


@pytest.mark.parametrize(
    'iterable, expected',
    [
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
    ],
)
def test_pairwise(iterable, expected):
    actual = pairwise(iterable)
    assert list(actual) == expected
