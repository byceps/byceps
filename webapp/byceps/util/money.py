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

    @classmethod
    def from_int(cls, value):
        if value < 0:
            raise ValueError

        euro, cent = divmod(value, 100)
        return cls(euro, cent)

    def to_int(self):
        return (self.euro * 100) + self.cent

    def to_str(self):
        return '{0.euro:d},{0.cent:02d}'.format(self)
