"""
byceps.services.news.news_item_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import dataclasses
from datetime import datetime
from functools import partial
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.sql import Select

from ...database import db, paginate, Pagination
from ...events.news import NewsItemPublished
from ...typing import UserID

from ..site import site_service
from ..site.transfer.models import SiteID
from ..user import user_service
from ..user.transfer.models import User

from .dbmodels.channel import DbChannel
from .dbmodels.item import DbCurrentVersionAssociation, DbItem, DbItemVersion
from . import news_channel_service, news_html_service, news_image_service
from .transfer.models import (
    BodyFormat,
    ChannelID,
    Headline,
    ImageID,
    Item,
    ItemID,
    ItemVersionID,
)


def create_item(
    channel_id: ChannelID,
    slug: str,
    creator_id: UserID,
    title: str,
    body: str,
    body_format: BodyFormat,
    *,
    image_url_path: Optional[str] = None,
) -> Item:
    """Create a news item, a version, and set the version as the item's
    current one.
    """
    db_item = DbItem(channel_id, slug)
    db.session.add(db_item)

    db_version = _create_version(
        db_item,
        creator_id,
        title,
        body,
        body_format,
        image_url_path=image_url_path,
    )
    db.session.add(db_version)

    db_current_version_association = DbCurrentVersionAssociation(
        db_item, db_version
    )
    db.session.add(db_current_version_association)

    db.session.commit()

    return _db_entity_to_item(db_item)


def update_item(
    item_id: ItemID,
    slug: str,
    creator_id: UserID,
    title: str,
    body: str,
    body_format: BodyFormat,
    *,
    image_url_path: Optional[str] = None,
) -> Item:
    """Update a news item by creating a new version of it and setting
    the new version as the current one.
    """
    db_item = _get_db_item(item_id)

    db_item.slug = slug

    db_version = _create_version(
        db_item,
        creator_id,
        title,
        body,
        body_format,
        image_url_path=image_url_path,
    )
    db.session.add(db_version)

    db_item.current_version = db_version

    db.session.commit()

    return _db_entity_to_item(db_item)


def _create_version(
    db_item: DbItem,
    creator_id: UserID,
    title: str,
    body: str,
    body_format: BodyFormat,
    *,
    image_url_path: Optional[str] = None,
) -> DbItemVersion:
    db_version = DbItemVersion(db_item, creator_id, title, body, body_format)

    if image_url_path:
        db_version.image_url_path = image_url_path

    return db_version


def set_featured_image(item_id: ItemID, image_id: ImageID) -> None:
    """Set an image as featured image."""
    db_item = _get_db_item(item_id)

    db_item.featured_image_id = image_id
    db.session.commit()


def publish_item(
    item_id: ItemID,
    *,
    publish_at: Optional[datetime] = None,
    initiator_id: Optional[UserID] = None,
) -> NewsItemPublished:
    """Publish a news item."""
    db_item = _get_db_item(item_id)

    if db_item.published:
        raise ValueError('News item has already been published')

    now = datetime.utcnow()
    if publish_at is None:
        publish_at = now

    initiator: Optional[User]
    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    db_item.published_at = publish_at
    db.session.commit()

    item = _db_entity_to_item(db_item)

    if item.channel.announcement_site_id is not None:
        site = site_service.get_site(SiteID(item.channel.announcement_site_id))
        external_url = f'https://{site.server_name}/news/{item.slug}'
    else:
        external_url = None

    return NewsItemPublished(
        occurred_at=now,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        item_id=item.id,
        channel_id=item.channel.id,
        published_at=publish_at,
        title=item.title,
        external_url=external_url,
    )


def unpublish_item(
    item_id: ItemID,
    *,
    initiator_id: Optional[UserID] = None,
) -> None:
    """Unublish a news item."""
    db_item = _get_db_item(item_id)

    if not db_item.published:
        raise ValueError('News item is not published')

    db_item.published_at = None
    db.session.commit()


def delete_item(item_id: ItemID) -> None:
    """Delete a news item and its versions."""
    db.session.execute(
        delete(DbCurrentVersionAssociation).where(
            DbCurrentVersionAssociation.item_id == item_id
        )
    )
    db.session.execute(
        delete(DbItemVersion).where(DbItemVersion.item_id == item_id)
    )
    db.session.execute(delete(DbItem).where(DbItem.id == item_id))
    db.session.commit()


def find_item(item_id: ItemID) -> Optional[Item]:
    """Return the item with that id, or `None` if not found."""
    db_item = _find_db_item(item_id)

    if db_item is None:
        return None

    return _db_entity_to_item(db_item)


def _find_db_item(item_id: ItemID) -> Optional[DbItem]:
    """Return the item with that id, or `None` if not found."""
    return (
        db.session.scalars(
            select(DbItem)
            .filter(DbItem.id == item_id)
            .options(
                db.joinedload(DbItem.channel), db.joinedload(DbItem.images)
            )
        )
        .unique()
        .one_or_none()
    )


def _get_db_item(item_id: ItemID) -> DbItem:
    """Return the item with that id, or raise an exception."""
    db_item = _find_db_item(item_id)

    if db_item is None:
        raise ValueError(f'Unknown news item ID "{item_id}".')

    return db_item


def find_aggregated_item_by_slug(
    channel_ids: set[ChannelID], slug: str, *, published_only: bool = False
) -> Optional[Item]:
    """Return the news item identified by that slug in one of the given
    channels, or `None` if not found.
    """
    stmt = (
        select(DbItem)
        .filter(DbItem.channel_id.in_(channel_ids))
        .filter_by(slug=slug)
        .options(
            db.joinedload(DbItem.channel),
            db.joinedload(DbItem.current_version_association).joinedload(
                DbCurrentVersionAssociation.version
            ),
            db.joinedload(DbItem.images),
        )
    )

    if published_only:
        stmt = stmt.filter(DbItem.published_at <= datetime.utcnow())

    db_item = db.session.scalars(stmt).unique().one_or_none()

    if db_item is None:
        return None

    return _db_entity_to_item(db_item, render_body=True)


def get_aggregated_items_paginated(
    channel_ids: set[ChannelID],
    page: int,
    items_per_page: int,
    *,
    published_only: bool = False,
) -> Pagination:
    """Return the news items to show on the specified page."""
    items_stmt = _get_items_stmt(channel_ids)
    count_stmt = _get_count_stmt(channel_ids)

    if published_only:
        items_stmt = items_stmt.filter(DbItem.published_at <= datetime.utcnow())
        count_stmt = count_stmt.filter(DbItem.published_at <= datetime.utcnow())

    item_mapper = partial(_db_entity_to_item, render_body=True)

    return paginate(
        items_stmt,
        count_stmt,
        page,
        items_per_page,
        scalar_result=True,
        unique_result=True,
        item_mapper=item_mapper,
    )


def get_items_paginated(
    channel_ids: set[ChannelID], page: int, items_per_page: int
) -> Pagination:
    """Return the news items to show on the specified page."""
    items_stmt = _get_items_stmt(channel_ids)
    count_stmt = _get_count_stmt(channel_ids)

    return paginate(
        items_stmt,
        count_stmt,
        page,
        items_per_page,
        scalar_result=True,
        unique_result=True,
    )


def get_headlines_paginated(
    channel_ids: set[ChannelID],
    page: int,
    items_per_page: int,
    *,
    published_only: bool = False,
) -> Pagination:
    """Return the headlines to show on the specified page."""
    items_stmt = (
        select(DbItem)
        .filter(DbItem.channel_id.in_(channel_ids))
        .options(
            db.joinedload(DbItem.current_version_association).joinedload(
                DbCurrentVersionAssociation.version
            )
        )
        .order_by(DbItem.published_at.desc())
    )

    count_stmt = _get_count_stmt(channel_ids)

    if published_only:
        items_stmt = items_stmt.filter(DbItem.published_at <= datetime.utcnow())
        count_stmt = count_stmt.filter(DbItem.published_at <= datetime.utcnow())

    return paginate(
        items_stmt,
        count_stmt,
        page,
        items_per_page,
        scalar_result=True,
        unique_result=True,
        item_mapper=_db_entity_to_headline,
    )


def get_recent_headlines(
    channel_ids: frozenset[ChannelID] | set[ChannelID], limit: int
) -> list[Headline]:
    """Return the most recent headlines."""
    db_items = db.session.scalars(
        select(DbItem)
        .filter(DbItem.channel_id.in_(channel_ids))
        .options(
            db.joinedload(DbItem.current_version_association).joinedload(
                DbCurrentVersionAssociation.version
            )
        )
        .filter(DbItem.published_at <= datetime.utcnow())
        .order_by(DbItem.published_at.desc())
        .limit(limit)
    ).all()

    return [_db_entity_to_headline(db_item) for db_item in db_items]


def _get_items_stmt(channel_ids: set[ChannelID]) -> Select:
    return (
        select(DbItem)
        .filter(DbItem.channel_id.in_(channel_ids))
        .options(
            db.joinedload(DbItem.channel),
            db.joinedload(DbItem.current_version_association).joinedload(
                DbCurrentVersionAssociation.version
            ),
            db.joinedload(DbItem.images),
        )
        .order_by(DbItem.published_at.desc())
    )


def _get_count_stmt(channel_ids: set[ChannelID]) -> Select:
    return select(db.func.count(DbItem.id)).filter(
        DbItem.channel_id.in_(channel_ids)
    )


def get_item_versions(item_id: ItemID) -> list[DbItemVersion]:
    """Return all item versions, sorted from most recent to oldest."""
    return db.session.scalars(
        select(DbItemVersion)
        .filter_by(item_id=item_id)
        .order_by(DbItemVersion.created_at.desc())
    ).all()


def get_current_item_version(item_id: ItemID) -> DbItemVersion:
    """Return the item's current version."""
    db_item = _get_db_item(item_id)

    return db_item.current_version


def find_item_version(version_id: ItemVersionID) -> DbItemVersion:
    """Return the item version with that ID, or `None` if not found."""
    return db.session.get(DbItemVersion, version_id)


def has_channel_items(channel_id: ChannelID) -> bool:
    """Return `True` if the channel contains items."""
    return db.session.scalar(
        select(
            select(DbItem)
            .join(DbChannel)
            .filter(DbChannel.id == channel_id)
            .exists()
        )
    )


def get_item_count_by_channel_id() -> dict[ChannelID, int]:
    """Return news item count (including 0) per channel, indexed by
    channel ID.
    """
    channel_ids_and_item_counts = db.session.execute(
        select(DbChannel.id, db.func.count(DbItem.id))
        .outerjoin(DbItem)
        .group_by(DbChannel.id)
    ).all()

    return dict(channel_ids_and_item_counts)


def _db_entity_to_item(
    db_item: DbItem, *, render_body: Optional[bool] = False
) -> Item:
    channel = news_channel_service._db_entity_to_channel(db_item.channel)

    image_url_path = _assemble_image_url_path(db_item)
    images = [
        news_image_service._db_entity_to_image(image, channel.id)
        for image in db_item.images
    ]

    item = Item(
        id=db_item.id,
        channel=channel,
        slug=db_item.slug,
        published_at=db_item.published_at,
        published=db_item.published_at is not None,
        title=db_item.current_version.title,
        body=db_item.current_version.body,
        body_format=db_item.current_version.body_format,
        image_url_path=image_url_path,
        images=images,
        featured_image_id=db_item.featured_image_id,
    )

    if render_body:
        rendered_body = _render_body(item)
        item = dataclasses.replace(item, body=rendered_body)

    return item


def _assemble_image_url_path(db_item: DbItem) -> Optional[str]:
    url_path = db_item.current_version.image_url_path

    if not url_path:
        return None

    return f'/data/global/news_channels/{db_item.channel_id}/{url_path}'


def _render_body(item: Item) -> Optional[str]:
    """Render body text to HTML."""
    try:
        return news_html_service.render_body(item, item.body, item.body_format)
    except Exception:
        return None  # Not the best error indicator.


def _db_entity_to_headline(db_item: DbItem) -> Headline:
    return Headline(
        slug=db_item.slug,
        published_at=db_item.published_at,
        published=db_item.published_at is not None,
        title=db_item.current_version.title,
    )
