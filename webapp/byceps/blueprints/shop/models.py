# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple


class EuroAmount(namedtuple('EuroAmount', ['euro', 'cent'])):

    @classmethod
    def from_int(cls, value):
        if value < 0:
            raise ValueError

        euro, cent = divmod(value, 100)
        return cls(euro, cent)
