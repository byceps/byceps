"""
byceps.services.shop.storefront.storefront_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.shop.catalog.models import CatalogID
from byceps.services.shop.order.models.number import OrderNumberSequenceID
from byceps.services.shop.shop.models import ShopID

from .dbmodels import DbStorefront
from .models import Storefront, StorefrontID


class UnknownStorefrontIdError(ValueError):
    pass


def create_storefront(
    storefront_id: StorefrontID,
    shop_id: ShopID,
    order_number_sequence_id: OrderNumberSequenceID,
    closed: bool,
    *,
    catalog_id: CatalogID | None = None,
) -> Storefront:
    """Create a storefront."""
    db_storefront = DbStorefront(
        storefront_id,
        shop_id,
        order_number_sequence_id,
        closed,
        catalog_id=catalog_id,
    )

    db.session.add(db_storefront)
    db.session.commit()

    return _db_entity_to_storefront(db_storefront)


def update_storefront(
    storefront_id: StorefrontID,
    catalog_id: CatalogID,
    order_number_sequence_id: OrderNumberSequenceID,
    closed: bool,
) -> Storefront:
    """Update a storefront."""
    db_storefront = _get_db_storefront(storefront_id)

    db_storefront.catalog_id = catalog_id
    db_storefront.order_number_sequence_id = order_number_sequence_id
    db_storefront.closed = closed

    db.session.commit()

    return _db_entity_to_storefront(db_storefront)


def delete_storefront(storefront_id: StorefrontID) -> None:
    """Delete a storefront."""
    db.session.execute(
        delete(DbStorefront).where(DbStorefront.id == storefront_id)
    )
    db.session.commit()


def find_storefront(storefront_id: StorefrontID) -> Storefront | None:
    """Return the storefront with that id, or `None` if not found."""
    db_storefront = _find_db_storefront(storefront_id)

    if db_storefront is None:
        return None

    return _db_entity_to_storefront(db_storefront)


def _find_db_storefront(storefront_id: StorefrontID) -> DbStorefront | None:
    """Return the database entity for the storefront with that id, or `None`
    if not found.
    """
    return db.session.get(DbStorefront, storefront_id)


def get_storefront(storefront_id: StorefrontID) -> Storefront:
    """Return the storefront with that id, or raise an exception."""
    storefront = find_storefront(storefront_id)

    if storefront is None:
        raise UnknownStorefrontIdError(storefront_id)

    return storefront


def _get_db_storefront(storefront_id: StorefrontID) -> DbStorefront:
    """Return the database entity for the storefront with that id.

    Raise an exception if not found.
    """
    db_storefront = _find_db_storefront(storefront_id)

    if db_storefront is None:
        raise UnknownStorefrontIdError(storefront_id)

    return db_storefront


def find_storefronts(storefront_ids: set[StorefrontID]) -> list[Storefront]:
    """Return the storefronts with those IDs."""
    if not storefront_ids:
        return []

    db_storefronts = db.session.scalars(
        select(DbStorefront).filter(DbStorefront.id.in_(storefront_ids))
    ).all()

    return [
        _db_entity_to_storefront(db_storefront)
        for db_storefront in db_storefronts
    ]


def get_all_storefronts() -> list[Storefront]:
    """Return all storefronts."""
    db_storefronts = db.session.scalars(select(DbStorefront)).all()

    return [
        _db_entity_to_storefront(db_storefront)
        for db_storefront in db_storefronts
    ]


def get_storefronts_for_shop(shop_id: ShopID) -> set[Storefront]:
    """Return all storefronts for that shop."""
    rows = db.session.scalars(
        select(DbStorefront).filter_by(shop_id=shop_id)
    ).all()

    return {_db_entity_to_storefront(row) for row in rows}


def _db_entity_to_storefront(db_storefront: DbStorefront) -> Storefront:
    return Storefront(
        id=db_storefront.id,
        shop_id=db_storefront.shop_id,
        catalog_id=db_storefront.catalog_id,
        order_number_sequence_id=db_storefront.order_number_sequence_id,
        closed=db_storefront.closed,
    )
