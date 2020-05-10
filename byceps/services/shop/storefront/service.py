"""
byceps.services.shop.storefront.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Set

from ....database import db

from ..sequence.transfer.models import NumberSequenceID
from ..shop.transfer.models import ShopID

from .models import Storefront as DbStorefront
from .transfer.models import Storefront, StorefrontID


class UnknownStorefrontId(ValueError):
    pass


def create_storefront(
    storefront_id: StorefrontID,
    shop_id: ShopID,
    order_number_sequence_id: NumberSequenceID,
    closed: bool,
) -> Storefront:
    """Create a storefront."""
    storefront = DbStorefront(
        storefront_id, shop_id, order_number_sequence_id, closed
    )

    db.session.add(storefront)
    db.session.commit()

    return _db_entity_to_storefront(storefront)


def delete_storefront(storefront_id: StorefrontID) -> None:
    """Delete a storefront."""
    db.session.query(DbStorefront) \
        .filter_by(id=storefront_id) \
        .delete()

    db.session.commit()


def find_storefront(storefront_id: StorefrontID) -> Optional[Storefront]:
    """Return the storefront with that id, or `None` if not found."""
    storefront = _find_db_storefront(storefront_id)

    if storefront is None:
        return None

    return _db_entity_to_storefront(storefront)


def _find_db_storefront(storefront_id: StorefrontID) -> Optional[DbStorefront]:
    """Return the database entity for the storefront with that id, or `None`
    if not found.
    """
    return DbStorefront.query.get(storefront_id)


def get_storefront(storefront_id: StorefrontID) -> Storefront:
    """Return the storefront with that id, or raise an exception."""
    storefront = find_storefront(storefront_id)

    if storefront is None:
        raise UnknownStorefrontId(storefront_id)

    return storefront


def _get_db_storefront(storefront_id: StorefrontID) -> DbStorefront:
    """Return the database entity for the storefront with that id.

    Raise an exception if not found.
    """
    storefront = _find_db_storefront(storefront_id)

    if storefront is None:
        raise UnknownStorefrontId(storefront_id)

    return storefront


def get_storefronts_for_shop(shop_id: ShopID) -> Set[Storefront]:
    """Return all storefronts for that shop."""
    rows = DbStorefront.query \
        .filter_by(shop_id=shop_id) \
        .all()

    return {_db_entity_to_storefront(row) for row in rows}


def _db_entity_to_storefront(storefront: DbStorefront) -> Storefront:
    return Storefront(
        storefront.id,
        storefront.shop_id,
        storefront.order_number_sequence_id,
        storefront.closed,
    )
