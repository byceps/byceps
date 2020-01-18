"""
testfixtures.brand
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.brand.models.brand import Brand


def create_brand(*, id='acmecon', title='Acme Entertainment Convention'):
    return Brand(id, title)
