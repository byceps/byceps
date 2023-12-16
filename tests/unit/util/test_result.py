"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.result import Err, Ok


@pytest.mark.parametrize(
    ('obj', 'f', 'expected'),
    [
        (Ok(23), lambda x: x * 2, Ok(23)),
        (Err(23), lambda x: x * 2, Err(46)),
    ],
)
def test_map_err(obj, f, expected):
    assert obj.map_err(f) == expected
