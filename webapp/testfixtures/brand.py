# -*- coding: utf-8 -*-

"""
testfixtures.brand
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.brand.models import Brand


def create_brand(*, id='acme', title='Acme Entertainment Convention'):
    return Brand(id, title)
