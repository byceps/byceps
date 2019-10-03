"""
testfixtures.party
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.services.party.models.party import Party

from .brand import create_brand


def create_party(
    *,
    id='acmecon-2014',
    brand_id=None,
    title='Acme Entertainment Convention 2014',
    shop_id=None,
):
    if brand_id is None:
        brand = create_brand()
        brand_id = brand.id

    starts_at = datetime(2014, 10, 24, 16, 0)
    ends_at = datetime(2014, 10, 26, 13, 0)

    return Party(id, brand_id, title, starts_at, ends_at, shop_id=shop_id)
