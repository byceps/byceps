"""
testfixtures.brand
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.brand.models.brand import Brand


def create_brand(*, id='acme', title='Acme Entertainment Convention'):
    return Brand(id, title)
