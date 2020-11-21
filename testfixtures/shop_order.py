"""
testfixtures.shop_order
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.models.orderer import Orderer


def create_orderer(user):
    return Orderer(
        user.id,
        user.detail.first_names,
        user.detail.last_name,
        user.detail.country,
        user.detail.zip_code,
        user.detail.city,
        user.detail.street,
    )
