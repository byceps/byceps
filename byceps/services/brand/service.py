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
from .transfer.models import BrandSetting


def create_brand(brand_id: BrandID, title: str) -> DbBrand:
    """Create a brand."""
    brand = DbBrand(brand_id, title)

    db.session.add(brand)
    db.session.commit()

    return brand


def find_brand(brand_id: BrandID) -> Optional[DbBrand]:
    """Return the brand with that id, or `None` if not found."""
    return DbBrand.query.get(brand_id)


def get_brands() -> List[DbBrand]:
    """Return all brands, ordered by title."""
    return DbBrand.query \
        .order_by(DbBrand.title) \
        .all()


def count_brands() -> int:
    """Return the number of brands."""
    return DbBrand.query.count()


def find_setting(brand_id: BrandID, name: str) -> Optional[BrandSetting]:
    """Return the setting for that brand and with that name, or `None`
    if not found.
    """
    setting = DbSetting.query.get((brand_id, name))

    if setting is None:
        return None

    return _db_entity_to_brand_setting(setting)


def _db_entity_to_brand_setting(setting: DbSetting) -> BrandSetting:
    return BrandSetting(
        setting.brand_id,
        setting.name,
        setting.value,
    )
