"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.util.iterables import find


@pytest.mark.parametrize(
    'predicate, iterable, expected',
    [
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
    ],
)
def test_find(predicate, iterable, expected):
    actual = find(predicate, iterable)
    assert actual == expected
