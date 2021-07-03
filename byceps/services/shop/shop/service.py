"""
byceps.services.shop.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ....database import db
from ....typing import BrandID

from .dbmodels import Shop as DbShop
from .transfer.models import Shop, ShopID


class UnknownShopId(ValueError):
    pass


def create_shop(shop_id: ShopID, brand_id: BrandID, title: str) -> Shop:
    """Create a shop."""
    shop = DbShop(shop_id, brand_id, title)

    db.session.add(shop)
    db.session.commit()

    return _db_entity_to_shop(shop)


def delete_shop(shop_id: ShopID) -> None:
    """Delete a shop."""
    db.session.query(DbShop) \
        .filter_by(id=shop_id) \
        .delete()

    db.session.commit()


def find_shop_for_brand(brand_id: BrandID) -> Optional[Shop]:
    """Return the shop for that brand, or `None` if not found."""
    shop = DbShop.query \
        .filter_by(brand_id=brand_id) \
        .one_or_none()

    if shop is None:
        return None

    return _db_entity_to_shop(shop)


def find_shop(shop_id: ShopID) -> Optional[Shop]:
    """Return the shop with that id, or `None` if not found."""
    shop = _find_db_shop(shop_id)

    if shop is None:
        return None

    return _db_entity_to_shop(shop)


def _find_db_shop(shop_id: ShopID) -> Optional[DbShop]:
    """Return the database entity for the shop with that id, or `None`
    if not found.
    """
    return db.session.query(DbShop).get(shop_id)


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
    shop = _find_db_shop(shop_id)

    if shop is None:
        raise UnknownShopId(shop_id)

    return shop


def find_shops(shop_ids: set[ShopID]) -> list[Shop]:
    """Return the shops with those IDs."""
    if not shop_ids:
        return []

    shops = DbShop.query \
        .filter(DbShop.id.in_(shop_ids)) \
        .all()

    return [_db_entity_to_shop(shop) for shop in shops]


def get_active_shops() -> list[Shop]:
    """Return all shops that are not archived."""
    shops = DbShop.query \
        .filter_by(archived=False) \
        .all()

    return [_db_entity_to_shop(shop) for shop in shops]


def set_extra_setting(shop_id: ShopID, key: str, value: str) -> None:
    """Set a value for a key in the shop's extra settings."""
    shop = _get_db_shop(shop_id)

    if shop.extra_settings is None:
        shop.extra_settings = {}

    shop.extra_settings[key] = value

    db.session.commit()


def remove_extra_setting(shop_id: ShopID, key: str) -> None:
    """Remove the entry with that key from the shop's extra settings."""
    shop = _get_db_shop(shop_id)

    if (shop.extra_settings is None) or (key not in shop.extra_settings):
        return

    del shop.extra_settings[key]

    db.session.commit()


def _db_entity_to_shop(shop: DbShop) -> Shop:
    settings = shop.extra_settings if (shop.extra_settings is not None) else {}

    return Shop(
        shop.id,
        shop.brand_id,
        shop.title,
        shop.archived,
        settings,
    )
