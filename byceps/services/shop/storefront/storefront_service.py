"""
byceps.services.shop.storefront.storefront_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.shop.catalog import catalog_service
from byceps.services.shop.catalog.models import Catalog
from byceps.services.shop.order.models.number import OrderNumberSequenceID
from byceps.services.shop.payment.models import PaymentGateway
from byceps.services.shop.shop.models import ShopID

from .dbmodels import DbStorefront
from .models import Storefront, StorefrontForAdmin, StorefrontID


class UnknownStorefrontIdError(ValueError):
    pass


def create_storefront(
    storefront_id: StorefrontID,
    shop_id: ShopID,
    order_number_sequence_id: OrderNumberSequenceID,
    closed: bool,
    *,
    catalog: Catalog | None = None,
) -> Storefront:
    """Create a storefront."""
    db_storefront = DbStorefront(
        storefront_id,
        shop_id,
        order_number_sequence_id,
        closed,
        catalog_id=catalog.id if catalog else None,
    )

    db.session.add(db_storefront)
    db.session.commit()

    return _db_entity_to_storefront(db_storefront, catalog)


def update_storefront(
    storefront_id: StorefrontID,
    catalog: Catalog | None,
    order_number_sequence_id: OrderNumberSequenceID,
    closed: bool,
) -> Storefront:
    """Update a storefront."""
    db_storefront = _get_db_storefront(storefront_id)

    db_storefront.catalog_id = catalog.id if catalog else None
    db_storefront.order_number_sequence_id = order_number_sequence_id
    db_storefront.closed = closed

    db.session.commit()

    return _db_entity_to_storefront(db_storefront, catalog)


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

    catalog = (
        catalog_service.find_catalog(db_storefront.catalog_id)
        if db_storefront.catalog_id
        else None
    )

    return _db_entity_to_storefront(db_storefront, catalog)


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
        select(DbStorefront)
        .options(db.joinedload(DbStorefront.catalog))
        .filter(DbStorefront.id.in_(storefront_ids))
    ).all()

    return [
        _db_entity_to_storefront(
            db_storefront,
            catalog=catalog_service._db_entity_to_catalog(db_storefront.catalog)
            if db_storefront.catalog
            else None,
        )
        for db_storefront in db_storefronts
    ]


def get_storefronts_for_shop(shop_id: ShopID) -> set[Storefront]:
    """Return all storefronts for that shop."""
    db_storefronts = db.session.scalars(
        select(DbStorefront)
        .options(db.joinedload(DbStorefront.catalog))
        .filter(DbStorefront.shop_id == shop_id)
    ).all()

    return {
        _db_entity_to_storefront(
            db_storefront,
            catalog=catalog_service._db_entity_to_catalog(db_storefront.catalog)
            if db_storefront.catalog
            else None,
        )
        for db_storefront in db_storefronts
    }


def _db_entity_to_storefront(
    db_storefront: DbStorefront, catalog: Catalog | None
) -> Storefront:
    return Storefront(
        id=db_storefront.id,
        shop_id=db_storefront.shop_id,
        catalog=catalog,
        order_number_sequence_id=db_storefront.order_number_sequence_id,
        closed=db_storefront.closed,
    )


def to_storefront_for_admin(
    storefront: Storefront,
    order_number_prefix: str,
    enabled_payment_gateways: set[PaymentGateway],
) -> StorefrontForAdmin:
    return StorefrontForAdmin(
        id=storefront.id,
        shop_id=storefront.shop_id,
        catalog=storefront.catalog,
        order_number_sequence_id=storefront.order_number_sequence_id,
        closed=storefront.closed,
        order_number_prefix=order_number_prefix,
        enabled_payment_gateways=enabled_payment_gateways,
    )


def to_storefronts_for_admin(
    storefronts: Iterable[Storefront],
    order_number_prefixes_by_sequence_id: dict[OrderNumberSequenceID, str],
    enabled_payment_gateways_by_storefront_id: dict[
        StorefrontID, set[PaymentGateway]
    ],
) -> list[StorefrontForAdmin]:
    return [
        to_storefront_for_admin(
            storefront,
            order_number_prefixes_by_sequence_id[
                storefront.order_number_sequence_id
            ],
            enabled_payment_gateways_by_storefront_id.get(storefront.id, set()),
        )
        for storefront in storefronts
    ]
