"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.result import Err, Ok


@pytest.mark.parametrize(
    ('result', 'f', 'expected'),
    [
        (Ok(23), lambda v: v * 2, Ok(23)),
        (Err(23), lambda v: v * 2, Err(46)),
    ],
)
def test_map_err(result, f, expected):
    assert result.map_err(f) == expected


@pytest.mark.parametrize(
    ('result', 'f', 'default', 'expected'),
    [
        (Ok(5), lambda v: v * 3, lambda e: 9, 15),
        (Err('Oops'), lambda v: v * 3, lambda e: 9, 9),
    ],
)
def test_map_or_else(result, f, default, expected):
    assert result.map_or_else(f, default) == expected
