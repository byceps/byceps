# -*- coding: utf-8 -*-

"""
testfixtures.party
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.services.party.models import Party

from .brand import create_brand


def create_party(*, id='acme-2014', brand=None,
                 title='Acme Entertainment Convention 2014'):
    if brand is None:
        brand = create_brand()

    starts_at = datetime(2014, 10, 24, 16, 0)
    ends_at = datetime(2014, 10, 26, 13, 0)

    return Party(id, brand.id, title, starts_at, ends_at)
