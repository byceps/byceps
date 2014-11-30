# -*- coding: utf-8 -*-

"""
byceps.util.money
~~~~~~~~~~~~~~~~~

Monetary amounts.

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple


class EuroAmount(namedtuple('EuroAmount', ['euro', 'cent'])):
    """A monetary amount in Euro.

    To create instances manually, use ``EuroAmount(39, 95)``.
    """

    def __add__(self, other):
        # Allow addition with integers. This is required for the `sum`
        # function to be applicable, which begings by adding `0` and
        # the first value).
        if isinstance(other, int):
            other = self.__class__.from_int(other)

        return self.__class__.from_int(self.to_int() + other.to_int())

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            raise TypeError('Instances of this class must only be multiplied '
                            'with integers, but not with each other.')

        return self.__class__.from_int(self.to_int() * other)

    @classmethod
    def from_int(cls, value):
        if value < 0:
            raise ValueError

        euro, cent = divmod(value, 100)
        return cls(euro, cent)

    def to_int(self):
        return (self.euro * 100) + self.cent

    def to_string(self):
        """Return a textual representation for display purposes only."""
        return '{0.euro:d},{0.cent:02d} €'.format(self)
