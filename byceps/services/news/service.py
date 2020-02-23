"""
byceps.services.news.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Optional, Sequence

from ...database import db, paginate, Pagination, Query
from ...events.news import NewsItemPublished
from ...typing import BrandID, UserID
from ...util.templating import load_template

from ..brand.models.brand import Brand as DbBrand

from .channel_service import _db_entity_to_channel
from .models.channel import Channel as DbChannel
from .models.item import (
    CurrentVersionAssociation as DbCurrentVersionAssociation,
    Item as DbItem,
    ItemVersion as DbItemVersion,
)
from . import image_service
from .transfer.models import ChannelID, Item, ItemID, ItemVersionID


def create_item(
    channel_id: ChannelID,
    slug: str,
    creator_id: UserID,
    title: str,
    body: str,
    *,
    image_url_path: Optional[str] = None,
) -> Item:
    """Create a news item, a version, and set the version as the item's
    current one.
    """
    item = DbItem(channel_id, slug)
    db.session.add(item)

    version = _create_version(
        item, creator_id, title, body, image_url_path=image_url_path
    )
    db.session.add(version)

    current_version_association = DbCurrentVersionAssociation(item, version)
    db.session.add(current_version_association)

    db.session.commit()

    return _db_entity_to_item(item)


def update_item(
    item_id: ItemID,
    slug: str,
    creator_id: UserID,
    title: str,
    body: str,
    *,
    image_url_path: Optional[str] = None,
) -> None:
    """Update a news item by creating a new version of it and setting
    the new version as the current one.
    """
    item = _get_db_item(item_id)

    item.slug = slug

    version = _create_version(
        item, creator_id, title, body, image_url_path=image_url_path
    )
    db.session.add(version)

    item.current_version = version

    db.session.commit()


def _create_version(
    item: DbItem,
    creator_id: UserID,
    title: str,
    body: str,
    *,
    image_url_path: Optional[str] = None,
) -> DbItemVersion:
    version = DbItemVersion(item, creator_id, title, body)

    if image_url_path:
        version.image_url_path = image_url_path

    return version


def publish_item(item_id: ItemID) -> NewsItemPublished:
    """Publish a news item."""
    item = _get_db_item(item_id)

    item.published_at = datetime.utcnow()
    db.session.commit()

    return NewsItemPublished(occurred_at=item.published_at, item_id=item.id)


def find_item(item_id: ItemID) -> Optional[Item]:
    """Return the item with that id, or `None` if not found."""
    item = _find_db_item(item_id)

    if item is None:
        return None

    return _db_entity_to_item(item)


def _find_db_item(item_id: ItemID) -> Optional[DbItem]:
    """Return the item with that id, or `None` if not found."""
    return DbItem.query \
        .with_channel() \
        .get(item_id)


def _get_db_item(item_id: ItemID) -> DbItem:
    """Return the item with that id, or raise an exception."""
    item = _find_db_item(item_id)

    if item is None:
        raise ValueError(f'Unknown news item ID "{item_id}".')

    return item


def find_aggregated_item_by_slug(
    channel_id: ChannelID, slug: str, *, published_only: bool = False
) -> Optional[Item]:
    """Return the news item identified by that slug, or `None` if not found."""
    query = DbItem.query \
        .for_channel(channel_id) \
        .with_channel() \
        .with_current_version() \
        .filter_by(slug=slug)

    if published_only:
        query = query.published()

    item = query.one_or_none()

    if item is None:
        return None

    return _db_entity_to_item(item)


def get_aggregated_items_paginated(
    channel_id: ChannelID,
    page: int,
    items_per_page: int,
    *,
    published_only: bool = False,
) -> Pagination:
    """Return the news items to show on the specified page."""
    query = _get_items_query(channel_id)

    if published_only:
        query = query.published()

    return paginate(query, page, items_per_page, item_mapper=_db_entity_to_item)


def get_items_paginated(
    channel_id: ChannelID, page: int, items_per_page: int
) -> Pagination:
    """Return the news items to show on the specified page."""
    return _get_items_query(channel_id) \
        .paginate(page, items_per_page)


def _get_items_query(channel_id: ChannelID) -> Query:
    return DbItem.query \
        .for_channel(channel_id) \
        .with_channel() \
        .with_current_version() \
        .order_by(DbItem.published_at.desc())


def get_item_versions(item_id: ItemID) -> Sequence[DbItemVersion]:
    """Return all item versions, sorted from most recent to oldest."""
    return DbItemVersion.query \
        .for_item(item_id) \
        .order_by(DbItemVersion.created_at.desc()) \
        .all()


def get_current_item_version(item_id: ItemID) -> DbItemVersion:
    """Return the item's current version."""
    item = _get_db_item(item_id)

    return item.current_version


def find_item_version(version_id: ItemVersionID) -> DbItemVersion:
    """Return the item version with that ID, or `None` if not found."""
    return DbItemVersion.query.get(version_id)


def count_items_for_brand(brand_id: BrandID) -> int:
    """Return the number of news items for that brand."""
    return DbItem.query \
        .join(DbChannel) \
        .filter(DbChannel.brand_id == brand_id) \
        .count()


def get_item_count_by_brand_id() -> Dict[BrandID, int]:
    """Return news item count (including 0) per brand, indexed by brand ID."""
    brand_ids_and_item_counts = db.session \
        .query(
            DbBrand.id,
            db.func.count(DbItem.id)
        ) \
        .outerjoin(DbChannel, DbChannel.brand_id == DbBrand.id) \
        .outerjoin(DbItem) \
        .group_by(DbBrand.id) \
        .all()

    return dict(brand_ids_and_item_counts)


def get_item_count_by_channel_id() -> Dict[ChannelID, int]:
    """Return news item count (including 0) per channel, indexed by
    channel ID.
    """
    channel_ids_and_item_counts = db.session \
        .query(
            DbChannel.id,
            db.func.count(DbItem.id)
        ) \
        .outerjoin(DbItem) \
        .group_by(DbChannel.id) \
        .all()

    return dict(channel_ids_and_item_counts)


def _db_entity_to_item(item: DbItem) -> Item:
    channel = _db_entity_to_channel(item.channel)
    external_url = item.channel.url_prefix + item.slug
    image_url_path = _assemble_image_url_path(item)
    images = [image_service._db_entity_to_image(image) for image in item.images]

    return Item(
        id=item.id,
        channel=channel,
        slug=item.slug,
        published_at=item.published_at,
        published=item.published_at is not None,
        title=item.current_version.title,
        body=item.current_version.body,
        external_url=external_url,
        image_url_path=image_url_path,
        images=images,
    )


def _assemble_image_url_path(item: DbItem) -> Optional[str]:
    url_path = item.current_version.image_url_path

    if not url_path:
        return None

    return f'/data/global/news_channels/{item.channel_id}/{url_path}'


def render_body(raw_body: str) -> str:
    """Render item's raw body to HTML."""
    template = load_template(raw_body)
    return template.render()
