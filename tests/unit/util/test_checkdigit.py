"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.util.checkdigit import calculate_check_digit


@pytest.mark.parametrize(
    'chars, expected',
    [
        ('12',         5),
        ('123',        0),
        ('1245496594', 3),
        ('TEST',       4),
        ('Test123',    7),
        ('00012',      5),
        ('9',          1),
        ('999',        3),
        ('999999',     6),
        ('CHECKDIGIT', 7),
        ('EK8XO5V9T8', 2),
        ('Y9IDV90NVK', 1),
        ('RWRGBM8C5S', 5),
        ('OBYY3LXR79', 5),
        ('Z2N9Z3F0K3', 2),
        ('ROBL3MPLSE', 9),
        ('VQWEWFNY8U', 9),
        ('45TPECUWKJ', 1),
        ('6KWKDFD79A', 8),
        ('HXNPKGY4EX', 3),
        ('91BT',       2),
    ],
)
def test_calculate_check_digit(chars, expected):
    assert calculate_check_digit(chars) == expected
