"""
byceps.services.currency.currency_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import CHF, Currency, DKK, EUR, GBP, NOK, SEK, USD


_CURRENCIES = [CHF, DKK, EUR, GBP, NOK, SEK, USD]


def get_currencies() -> list[Currency]:
    """Return list of supported currencies."""
    return _CURRENCIES
