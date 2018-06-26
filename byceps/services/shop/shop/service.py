"""
byceps.services.shop.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ....database import db
from ....typing import PartyID

from .models import Shop as DbShop
from .transfer.models import Shop, ShopID


def create_shop(party_id: PartyID) -> Shop:
    """Create a shop."""
    shop = DbShop(party_id, party_id)

    db.session.add(shop)
    db.session.commit()

    return _db_entity_to_shop(shop)


def find_shop(shop_id: ShopID) -> Optional[Shop]:
    """Return the shop with that id, or `None` if not found."""
    shop = DbShop.query.get(shop_id)

    if shop is None:
        return None

    return _db_entity_to_shop(shop)


def _db_entity_to_shop(shop: DbShop) -> Shop:
    return Shop(
        shop.id,
        shop.party_id,
    )
