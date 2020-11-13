"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

import pytest

from byceps.util.money import to_two_places


@pytest.mark.parametrize(
    'value, expected',
    [
        (Decimal(       '0'), Decimal(  '0.00')),
        (Decimal(     '0.1'), Decimal(  '0.10')),
        (Decimal(    '0.01'), Decimal(  '0.01')),
        (Decimal(  '0.1234'), Decimal(  '0.12')),
        (Decimal(   '0.009'), Decimal(  '0.01')),
        (Decimal('123.4500'), Decimal('123.45')),
        (Decimal('123.4567'), Decimal('123.46')),
    ],
)
def test_to_two_places(value, expected):
    assert to_two_places(value) == expected
