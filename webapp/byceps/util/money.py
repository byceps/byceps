# -*- coding: utf-8 -*-

"""
byceps.util.money
~~~~~~~~~~~~~~~~~

Monetary amounts.

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from decimal import Decimal
import locale


TWO_PLACES = Decimal('.00')


def register_template_filters(app):
    """Make functions available as template filters."""
    app.add_template_filter(format_euro_amount)


def format_euro_amount(x):
    """Return a textual representation with two decimal places,
    locale-specific decimal point and thousands separators, and the Euro
    symbol.
    """
    quantized = to_two_places(x)
    formatted_number = locale.format('%.2f', float(quantized), grouping=True)
    return '{} €'.format(formatted_number)


class EuroAmount(namedtuple('EuroAmount', ['euro', 'cent'])):
    """A monetary amount in Euro.

    To create instances manually, use ``EuroAmount(39, 95)``.
    """

    def __add__(self, other):
        # Allow addition with integers. This is required for the `sum`
        # function to be applicable, which begins by adding `0` and the
        # first value).
        if isinstance(other, int):
            other = self.__class__.from_int(other)

        return self.__class__.from_int(self.to_int() + other.to_int())

    def __radd__(self, other):
        # Required for the `sum` function to be applicable.
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            raise TypeError('Instances of this class must only be multiplied '
                            'with integers, but not with each other.')

        return self.__class__.from_int(self.to_int() * other)

    @classmethod
    def from_decimal(cls, value):
        if value < Decimal('0'):
            raise ValueError

        quantized = to_two_places(value)
        euro, cent = map(int, str(quantized).partition('.')[::2])

        return cls(euro, cent)

    @classmethod
    def from_int(cls, value):
        if value < 0:
            raise ValueError

        euro, cent = divmod(value, 100)
        return cls(euro, cent)

    def to_decimal(self):
        value = '{0.euro}.{0.cent:02d}'.format(self)
        return Decimal(value)

    def to_int(self):
        return (self.euro * 100) + self.cent


def to_two_places(x):
    """Quantize to two decimal places."""
    return x.quantize(TWO_PLACES)
