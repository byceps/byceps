"""
byceps.services.news.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import BrandID, UserID

from ..brand.models.brand import Brand

from .models import CurrentVersionAssociation, Item, ItemID, ItemVersion, \
    ItemVersionID


def create_item(brand_id: BrandID, slug: str, creator_id: UserID, title: str,
                body: str, *, image_url_path: Optional[str]=None) -> Item:
    """Create a news item, a version, and set the version as the item's
    current one.
    """
    item = Item(brand_id, slug)
    db.session.add(item)

    version = _create_version(item, creator_id, title, body,
                              image_url_path=image_url_path)
    db.session.add(version)

    current_version_association = CurrentVersionAssociation(item, version)
    db.session.add(current_version_association)

    db.session.commit()

    return item


def update_item(item: Item, creator_id: UserID, title: str, body: str, *,
                image_url_path: Optional[str]=None) -> None:
    """Update a news item by creating a new version of it and setting
    the new version as the current one.
    """
    version = _create_version(item, creator_id, title, body,
                              image_url_path=image_url_path)
    db.session.add(version)

    item.current_version = version

    db.session.commit()


def _create_version(item: Item, creator_id: UserID, title: str, body: str, *,
                    image_url_path: Optional[str]=None) -> ItemVersion:
    version = ItemVersion(item, creator_id, title, body)

    if image_url_path:
        version.image_url_path = image_url_path

    return version


def find_item(item_id: ItemID) -> Optional[Item]:
    """Return the item with that id, or `None` if not found."""
    return Item.query.get(item_id)


def find_item_by_slug(brand_id: BrandID, slug: str) -> Optional[Item]:
    """Return the news item identified by that slug, or `None` if not found."""
    return Item.query \
        .for_brand_id(brand_id) \
        .with_current_version() \
        .filter_by(slug=slug) \
        .first()


def get_items_paginated(brand_id: BrandID, page: int, items_per_page: int,
                        published_only: bool=False
                       ) -> Pagination:
    """Return the news items to show on the specified page."""
    query = Item.query \
        .for_brand_id(brand_id) \
        .with_current_version()

    if published_only:
        query = query.published()

    return query \
        .order_by(Item.published_at.desc()) \
        .paginate(page, items_per_page)


def find_item_version(version_id: ItemVersionID) -> ItemVersion:
    """Return the item version with that ID, or `None` if not found."""
    return ItemVersion.query.get(version_id)


def count_items_for_brand(brand_id: BrandID) -> int:
    """Return the number of news items for that brand."""
    return Item.query \
        .for_brand_id(brand_id) \
        .count()


def get_item_count_by_brand_id() -> Dict[BrandID, int]:
    """Return news item count (including 0) per brand, indexed by brand ID."""
    return dict(db.session \
        .query(
            Brand.id,
            db.func.count(Item.brand_id)
        ) \
        .outerjoin(Item) \
        .group_by(Brand.id) \
        .all())
