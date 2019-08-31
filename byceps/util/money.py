"""
byceps.util.money
~~~~~~~~~~~~~~~~~

Handle monetary amounts.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal
import locale


TWO_PLACES = Decimal('.00')


def format_euro_amount(x: Decimal) -> str:
    """Return a textual representation with two decimal places,
    locale-specific decimal point and thousands separators, and the Euro
    symbol.
    """
    quantized = to_two_places(x)
    formatted_number = locale.format_string('%.2f', quantized, grouping=True)
    return f'{formatted_number} €'


def to_two_places(x: Decimal) -> Decimal:
    """Quantize to two decimal places."""
    return x.quantize(TWO_PLACES)
