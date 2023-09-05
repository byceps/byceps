"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import os
from typing import Any

import pytest

from byceps.config import parse_value_from_environment


@pytest.mark.parametrize(
    ('key', 'value', 'expected'),
    [
        ('BOOLEAN_TRUE', 'true', True),
        ('BOOLEAN_FALSE', 'false', False),
        ('DICT', '{"one": 1, "two": 2}', {'one': 1, 'two': 2}),
        ('FLOAT', '3.14', 3.14),
        ('FLOAT_INVALID', '3.14P', '3.14P'),
        ('INTEGER', '42', 42),
        ('INTEGER_INVALID', '12xy', '12xy'),
        ('LIST', '[4, 8, 15, 16, 23, 42]', [4, 8, 15, 16, 23, 42]),
        ('NONE', 'null', None),
        ('STRING', '"hello world"', 'hello world'),
    ],
)
def test_parse_value_from_environment(key: str, value: str, expected: Any):
    os.environ[key] = value

    assert parse_value_from_environment(key) == expected


def test_parse_value_from_environment_for_missing_key():
    key = 'missing'
    assert key not in os.environ

    assert parse_value_from_environment(key) is None
