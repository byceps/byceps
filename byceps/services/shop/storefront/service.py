"""
byceps.services.shop.storefront.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ....database import db

from ..catalog.transfer.models import CatalogID
from ..order.transfer.models.number import OrderNumberSequenceID
from ..shop.transfer.models import ShopID

from .dbmodels import Storefront as DbStorefront
from .transfer.models import Storefront, StorefrontID


class UnknownStorefrontId(ValueError):
    pass


def create_storefront(
    storefront_id: StorefrontID,
    shop_id: ShopID,
    order_number_sequence_id: OrderNumberSequenceID,
    closed: bool,
    *,
    catalog_id: Optional[CatalogID] = None,
) -> Storefront:
    """Create a storefront."""
    storefront = DbStorefront(
        storefront_id,
        shop_id,
        order_number_sequence_id,
        closed,
        catalog_id=catalog_id,
    )

    db.session.add(storefront)
    db.session.commit()

    return _db_entity_to_storefront(storefront)


def update_storefront(
    storefront_id: StorefrontID,
    catalog_id: CatalogID,
    order_number_sequence_id: OrderNumberSequenceID,
    closed: bool,
) -> Storefront:
    """Update a storefront."""
    storefront = _get_db_storefront(storefront_id)

    storefront.catalog_id = catalog_id
    storefront.order_number_sequence_id = order_number_sequence_id
    storefront.closed = closed

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
    return db.session.query(DbStorefront).get(storefront_id)


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


def find_storefronts(storefront_ids: set[StorefrontID]) -> list[Storefront]:
    """Return the storefronts with those IDs."""
    if not storefront_ids:
        return []

    storefronts = db.session \
        .query(DbStorefront) \
        .filter(DbStorefront.id.in_(storefront_ids)) \
        .all()

    return [_db_entity_to_storefront(storefront) for storefront in storefronts]


def get_all_storefronts() -> list[Storefront]:
    """Return all storefronts."""
    storefronts = db.session.query(DbStorefront).all()

    return [_db_entity_to_storefront(storefront) for storefront in storefronts]


def get_storefronts_for_shop(shop_id: ShopID) -> set[Storefront]:
    """Return all storefronts for that shop."""
    rows = db.session \
        .query(DbStorefront) \
        .filter_by(shop_id=shop_id) \
        .all()

    return {_db_entity_to_storefront(row) for row in rows}


def _db_entity_to_storefront(storefront: DbStorefront) -> Storefront:
    return Storefront(
        storefront.id,
        storefront.shop_id,
        storefront.catalog_id,
        storefront.order_number_sequence_id,
        storefront.closed,
    )
