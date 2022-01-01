"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.iterables import partition


@pytest.mark.parametrize(
    'iterable, predicate, expected',
    [
        (
            [],
            lambda x: x > 3,
            ([], []),
        ),
        (
            [0, 1, 2, 3, 4, 5, 6, 7],
            lambda x: x % 3 == 0,
            ([0, 3, 6], [1, 2, 4, 5, 7]),
        ),
    ],
)
def test_partition(iterable, predicate, expected):
    actual = partition(iterable, predicate)
    assert actual == expected
