"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

import pytest

from byceps.util.l10n import set_locale
from byceps.util.money import format_euro_amount


@pytest.mark.parametrize(
    'value, expected',
    [
        (Decimal(      '0.00' ),         '0,00 €'),
        (Decimal(      '0.01' ),         '0,01 €'),
        (Decimal(      '0.5'  ),         '0,50 €'),
        (Decimal(      '1.23' ),         '1,23 €'),
        (Decimal(    '123.45' ),       '123,45 €'),
        (Decimal(    '123.456'),       '123,46 €'),
        (Decimal('1234567'    ), '1.234.567,00 €'),
        (Decimal('1234567.89' ), '1.234.567,89 €'),
    ],
)
def test_format_euro_amount(value, expected):
    set_locale('de_DE.UTF-8')

    assert format_euro_amount(value) == expected
