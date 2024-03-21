"""
:Copyright: 2014-2024 Jochen Kupperschmidt
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
