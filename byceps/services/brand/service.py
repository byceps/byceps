"""
byceps.services.brand.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...typing import BrandID
from ...database import db

from .models.brand import Brand as DbBrand
from .models.setting import Setting as DbSetting
from .transfer.models import Brand, BrandSetting


def create_brand(brand_id: BrandID, title: str) -> Brand:
    """Create a brand."""
    brand = DbBrand(brand_id, title)

    db.session.add(brand)
    db.session.commit()

    return _db_entity_to_brand(brand)


def find_brand(brand_id: BrandID) -> Optional[Brand]:
    """Return the brand with that id, or `None` if not found."""
    brand = DbBrand.query.get(brand_id)

    if brand is None:
        return None

    return _db_entity_to_brand(brand)


def get_brands() -> List[Brand]:
    """Return all brands, ordered by title."""
    brands = DbBrand.query \
        .order_by(DbBrand.title) \
        .all()

    return [_db_entity_to_brand(brand) for brand in brands]


def count_brands() -> int:
    """Return the number of brands."""
    return DbBrand.query.count()


def create_setting(brand_id: BrandID, name: str, value: str) -> BrandSetting:
    """Create a setting for that brand."""
    setting = DbSetting(brand_id, name, value)

    db.session.add(setting)
    db.session.commit()

    return _db_entity_to_brand_setting(setting)


def find_setting(brand_id: BrandID, name: str) -> Optional[BrandSetting]:
    """Return the setting for that brand and with that name, or `None`
    if not found.
    """
    setting = DbSetting.query.get((brand_id, name))

    if setting is None:
        return None

    return _db_entity_to_brand_setting(setting)


def find_setting_value(brand_id: BrandID, name: str) -> Optional[str]:
    """Return the value of the setting for that brand and with that
    name, or `None` if not found.
    """
    setting = find_setting(brand_id, name)

    if setting is None:
        return None

    return setting.value


def _db_entity_to_brand(brand: DbBrand) -> Brand:
    return Brand(
        brand.id,
        brand.title,
    )


def _db_entity_to_brand_setting(setting: DbSetting) -> BrandSetting:
    return BrandSetting(
        setting.brand_id,
        setting.name,
        setting.value,
    )
