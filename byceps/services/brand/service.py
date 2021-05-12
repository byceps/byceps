"""
byceps.services.brand.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db
from ...typing import BrandID

from .dbmodels.brand import Brand as DbBrand
from .dbmodels.setting import Setting as DbSetting
from .transfer.models import Brand


def create_brand(brand_id: BrandID, title: str) -> Brand:
    """Create a brand."""
    brand = DbBrand(brand_id, title)

    db.session.add(brand)
    db.session.commit()

    return _db_entity_to_brand(brand)


def update_brand(
    brand_id: BrandID, title: str, image_filename: Optional[str]
) -> Brand:
    """Update a brand."""
    brand = _get_db_brand(brand_id)

    brand.title = title
    brand.image_filename = image_filename

    db.session.commit()

    return _db_entity_to_brand(brand)


def delete_brand(brand_id: BrandID) -> None:
    """Delete a brand."""
    db.session.query(DbSetting) \
        .filter_by(brand_id=brand_id) \
        .delete()

    db.session.query(DbBrand) \
        .filter_by(id=brand_id) \
        .delete()

    db.session.commit()


def find_brand(brand_id: BrandID) -> Optional[Brand]:
    """Return the brand with that id, or `None` if not found."""
    brand = _get_db_brand(brand_id)

    if brand is None:
        return None

    return _db_entity_to_brand(brand)


def _get_db_brand(brand_id: BrandID) -> DbBrand:
    """Return the brand with that ID."""
    return DbBrand.query.get(brand_id)


def get_brand(brand_id: BrandID) -> Brand:
    """Return the brand with that id, or raise an exception."""
    brand = find_brand(brand_id)

    if brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    return brand


def get_all_brands() -> list[Brand]:
    """Return all brands, ordered by title."""
    brands = DbBrand.query \
        .order_by(DbBrand.title) \
        .all()

    return [_db_entity_to_brand(brand) for brand in brands]


def count_brands() -> int:
    """Return the number of brands."""
    return DbBrand.query.count()


def _db_entity_to_brand(brand: DbBrand) -> Brand:
    if brand.image_filename:
        image_url_path = f'/data/global/brand_images/{brand.image_filename}'
    else:
        image_url_path = None

    return Brand(
        brand.id,
        brand.title,
        brand.image_filename,
        image_url_path,
    )
