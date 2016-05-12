# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.models.country
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple


Country = namedtuple('Country', 'name alpha2 alpha3')
