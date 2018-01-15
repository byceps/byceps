"""
byceps.services.brand.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...typing import BrandID
from ...database import db

from .models.brand import Brand
from .models.setting import Setting, SettingTuple


def create_brand(brand_id: BrandID, title: str) -> Brand:
    """Create a brand."""
    brand = Brand(brand_id, title)

    db.session.add(brand)
    db.session.commit()

    return brand


def find_brand(brand_id: BrandID) -> Optional[Brand]:
    """Return the brand with that id, or `None` if not found."""
    return Brand.query.get(brand_id)


def get_brands() -> List[Brand]:
    """Return all brands, ordered by title."""
    return Brand.query \
        .order_by(Brand.title) \
        .all()


def count_brands() -> int:
    """Return the number of brands."""
    return Brand.query.count()


def find_setting(brand_id: BrandID, name: str) -> Optional[SettingTuple]:
    """Return the setting for that brand and with that name, or `None`
    if not found.
    """
    setting = Setting.query.get((brand_id, name))

    if setting is None:
        return None

    return setting.to_tuple()
