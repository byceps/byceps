"""
byceps.services.shop.shop.shop_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from moneyed import Currency
from sqlalchemy import delete, select

from byceps.database import db
from byceps.typing import BrandID

from .dbmodels import DbShop
from .models import Shop, ShopID


class UnknownShopId(ValueError):
    pass


def create_shop(
    shop_id: ShopID, brand_id: BrandID, title: str, currency: Currency
) -> Shop:
    """Create a shop."""
    db_shop = DbShop(shop_id, brand_id, title, currency)

    db.session.add(db_shop)
    db.session.commit()

    return _db_entity_to_shop(db_shop)


def delete_shop(shop_id: ShopID) -> None:
    """Delete a shop."""
    db.session.execute(delete(DbShop).where(DbShop.id == shop_id))
    db.session.commit()


def find_shop_for_brand(brand_id: BrandID) -> Shop | None:
    """Return the shop for that brand, or `None` if not found."""
    db_shop = db.session.execute(
        select(DbShop).filter_by(brand_id=brand_id)
    ).scalar_one_or_none()

    if db_shop is None:
        return None

    return _db_entity_to_shop(db_shop)


def find_shop(shop_id: ShopID) -> Shop | None:
    """Return the shop with that id, or `None` if not found."""
    db_shop = _find_db_shop(shop_id)

    if db_shop is None:
        return None

    return _db_entity_to_shop(db_shop)


def _find_db_shop(shop_id: ShopID) -> DbShop | None:
    """Return the database entity for the shop with that id, or `None`
    if not found.
    """
    return db.session.get(DbShop, shop_id)


def get_shop(shop_id: ShopID) -> Shop:
    """Return the shop with that id, or raise an exception."""
    shop = find_shop(shop_id)

    if shop is None:
        raise UnknownShopId(shop_id)

    return shop


def _get_db_shop(shop_id: ShopID) -> DbShop:
    """Return the database entity for the shop with that id.

    Raise an exception if not found.
    """
    db_shop = _find_db_shop(shop_id)

    if db_shop is None:
        raise UnknownShopId(shop_id)

    return db_shop


def find_shops(shop_ids: set[ShopID]) -> list[Shop]:
    """Return the shops with those IDs."""
    if not shop_ids:
        return []

    db_shops = db.session.scalars(
        select(DbShop).filter(DbShop.id.in_(shop_ids))
    ).all()

    return [_db_entity_to_shop(db_shop) for db_shop in db_shops]


def get_active_shops() -> list[Shop]:
    """Return all shops that are not archived."""
    db_shops = db.session.scalars(
        select(DbShop).filter_by(archived=False)
    ).all()

    return [_db_entity_to_shop(db_shop) for db_shop in db_shops]


def set_extra_setting(shop_id: ShopID, key: str, value: str) -> None:
    """Set a value for a key in the shop's extra settings."""
    db_shop = _get_db_shop(shop_id)

    if db_shop.extra_settings is None:
        db_shop.extra_settings = {}

    db_shop.extra_settings[key] = value

    db.session.commit()


def remove_extra_setting(shop_id: ShopID, key: str) -> None:
    """Remove the entry with that key from the shop's extra settings."""
    db_shop = _get_db_shop(shop_id)

    if (db_shop.extra_settings is None) or (key not in db_shop.extra_settings):
        return

    del db_shop.extra_settings[key]

    db.session.commit()


def _db_entity_to_shop(db_shop: DbShop) -> Shop:
    settings = (
        db_shop.extra_settings if (db_shop.extra_settings is not None) else {}
    )

    return Shop(
        id=db_shop.id,
        brand_id=db_shop.brand_id,
        title=db_shop.title,
        currency=db_shop.currency,
        archived=db_shop.archived,
        extra_settings=settings,
    )
