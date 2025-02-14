"""
byceps.services.brand.brand_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.brand.models import BrandID
from byceps.services.newsletter import newsletter_service
from byceps.services.newsletter.models import (
    List as NewsletterList,
    ListID as NewsletterListID,
)

from . import brand_setting_service
from .dbmodels import DbBrand, DbBrandSetting
from .models import Brand


def create_brand(brand_id: BrandID, title: str) -> Brand:
    """Create a brand."""
    db_brand = DbBrand(brand_id, title)

    db.session.add(db_brand)
    db.session.commit()

    return _db_entity_to_brand(db_brand)


def update_brand(
    brand_id: BrandID,
    title: str,
    image_filename: str | None,
    archived: bool,
) -> Brand:
    """Update a brand."""
    db_brand = _find_db_brand(brand_id)

    if db_brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    db_brand.title = title
    db_brand.image_filename = image_filename
    db_brand.archived = archived

    db.session.commit()

    return _db_entity_to_brand(db_brand)


def delete_brand(brand_id: BrandID) -> None:
    """Delete a brand."""
    db.session.execute(delete(DbBrandSetting).filter_by(brand_id=brand_id))
    db.session.execute(delete(DbBrand).filter_by(id=brand_id))
    db.session.commit()


def find_brand(brand_id: BrandID) -> Brand | None:
    """Return the brand with that id, or `None` if not found."""
    db_brand = _find_db_brand(brand_id)

    if db_brand is None:
        return None

    return _db_entity_to_brand(db_brand)


def _find_db_brand(brand_id: BrandID) -> DbBrand | None:
    """Return the brand with that ID, or `None` if not found."""
    return db.session.get(DbBrand, brand_id)


def find_brand_by_title(title: str) -> Brand | None:
    """Return the brand with that title, or `None` if not found."""
    db_brand = db.session.scalar(select(DbBrand).filter_by(title=title))

    if db_brand is None:
        return None

    return _db_entity_to_brand(db_brand)


def get_brand(brand_id: BrandID) -> Brand:
    """Return the brand with that id, or raise an exception."""
    brand = find_brand(brand_id)

    if brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    return brand


def get_all_brands() -> list[Brand]:
    """Return all brands, ordered by title."""
    db_brands = db.session.scalars(
        select(DbBrand).order_by(DbBrand.title)
    ).all()

    return [_db_entity_to_brand(db_brand) for db_brand in db_brands]


def get_active_brands() -> set[Brand]:
    """Return active (i.e. non-archived) brands."""
    db_brands = db.session.scalars(
        select(DbBrand).filter_by(archived=False)
    ).all()

    return {_db_entity_to_brand(db_brand) for db_brand in db_brands}


def count_brands() -> int:
    """Return the number of brands."""
    return db.session.scalar(select(db.func.count(DbBrand.id))) or 0


def _db_entity_to_brand(db_brand: DbBrand) -> Brand:
    image_url_path: str | None
    if db_brand.image_filename:
        image_url_path = f'/data/global/brand_images/{db_brand.image_filename}'
    else:
        image_url_path = None

    return Brand(
        id=db_brand.id,
        title=db_brand.title,
        image_filename=db_brand.image_filename,
        image_url_path=image_url_path,
        archived=db_brand.archived,
    )


def find_newsletter_list_for_brand(brand_id: BrandID) -> NewsletterList | None:
    """Return the newsletter list configured for this brand, or `None`
    if none is configured.
    """
    list_id = brand_setting_service.find_setting_value(
        brand_id, 'newsletter_list_id'
    )

    if not list_id:
        return None

    return newsletter_service.find_list(NewsletterListID(list_id))
