"""
byceps.services.news.news_item_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
import dataclasses
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.sql import Select
import structlog

from byceps.database import db, paginate, Pagination, execute_upsert
from byceps.services.brand.models import BrandID
from byceps.services.core.events import EventUser
from byceps.services.site import site_service
from byceps.services.site.models import SiteID
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import news_channel_service, news_html_service, news_image_service
from .dbmodels import (
    DbCurrentNewsItemVersionAssociation,
    DbFeaturedNewsImage,
    DbNewsChannel,
    DbNewsItem,
    DbNewsItemVersion,
)
from .events import NewsItemPublishedEvent
from .models import (
    AdminListNewsItem,
    BodyFormat,
    NewsChannel,
    NewsChannelID,
    NewsHeadline,
    NewsImage,
    NewsImageID,
    NewsItem,
    NewsItemID,
    NewsItemVersionID,
    NewsTeaser,
    RenderedNewsItem,
)


log = structlog.get_logger()


def create_item(
    channel: NewsChannel,
    slug: str,
    creator: User,
    title: str,
    body: str,
    body_format: BodyFormat,
) -> NewsItem:
    """Create a news item, a version, and set the version as the item's
    current one.
    """
    db_item = DbNewsItem(channel.brand_id, channel.id, slug)
    db.session.add(db_item)

    db_version = _create_version(
        db_item,
        creator,
        title,
        body,
        body_format,
    )
    db.session.add(db_version)

    db_current_version_association = DbCurrentNewsItemVersionAssociation(
        db_item, db_version
    )
    db.session.add(db_current_version_association)

    db.session.commit()

    return _db_entity_to_item(db_item)


def update_item(
    item_id: NewsItemID,
    slug: str,
    creator: User,
    title: str,
    body: str,
    body_format: BodyFormat,
) -> NewsItem:
    """Update a news item by creating a new version of it and setting
    the new version as the current one.
    """
    db_item = _get_db_item(item_id)

    db_item.slug = slug

    db_version = _create_version(
        db_item,
        creator,
        title,
        body,
        body_format,
    )
    db.session.add(db_version)

    db_item.current_version = db_version

    db.session.commit()

    return _db_entity_to_item(db_item)


def _create_version(
    db_item: DbNewsItem,
    creator: User,
    title: str,
    body: str,
    body_format: BodyFormat,
) -> DbNewsItemVersion:
    return DbNewsItemVersion(db_item, creator.id, title, body, body_format)


def set_featured_image(item_id: NewsItemID, image_id: NewsImageID) -> None:
    """Set an image as featured image."""
    db_item = _get_db_item(item_id)

    table = DbFeaturedNewsImage.__table__
    identifier = {'item_id': db_item.id, 'image_id': image_id}
    replacement = {'image_id': image_id}
    execute_upsert(table, identifier, replacement)

    db.session.commit()


def unset_featured_image(item_id: NewsItemID) -> None:
    """Unset a featured image."""
    db_item = _get_db_item(item_id)

    db.session.execute(
        delete(DbFeaturedNewsImage).where(
            DbFeaturedNewsImage.item_id == db_item.id
        )
    )
    db.session.commit()


def publish_item(
    item_id: NewsItemID,
    *,
    publish_at: datetime | None = None,
    initiator: User | None = None,
) -> Result[NewsItemPublishedEvent, str]:
    """Publish a news item."""
    db_item = _get_db_item(item_id)

    if db_item.published:
        return Err('News item has already been published')

    now = datetime.utcnow()
    if publish_at is None:
        publish_at = now

    db_item.published_at = publish_at
    db.session.commit()

    item = _db_entity_to_item(db_item)

    if item.channel.announcement_site_id is not None:
        site = site_service.get_site(SiteID(item.channel.announcement_site_id))
        external_url = f'https://{site.server_name}/news/{item.slug}'
    else:
        external_url = None

    event = NewsItemPublishedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(initiator) if initiator else None,
        item_id=item.id,
        channel_id=item.channel.id,
        published_at=publish_at,
        title=item.title,
        external_url=external_url,
    )

    return Ok(event)


def unpublish_item(
    item_id: NewsItemID,
    *,
    initiator: User | None = None,
) -> Result[None, str]:
    """Unublish a news item."""
    db_item = _get_db_item(item_id)

    if not db_item.published:
        return Err('News item is not published')

    db_item.published_at = None
    db.session.commit()

    return Ok(None)


def delete_item(item_id: NewsItemID) -> None:
    """Delete a news item and its versions."""
    db.session.execute(
        delete(DbCurrentNewsItemVersionAssociation).where(
            DbCurrentNewsItemVersionAssociation.item_id == item_id
        )
    )
    db.session.execute(
        delete(DbNewsItemVersion).where(DbNewsItemVersion.item_id == item_id)
    )
    db.session.execute(delete(DbNewsItem).where(DbNewsItem.id == item_id))
    db.session.commit()


def find_item(item_id: NewsItemID) -> NewsItem | None:
    """Return the item with that id, or `None` if not found."""
    db_item = _find_db_item(item_id)

    if db_item is None:
        return None

    return _db_entity_to_item(db_item)


def _find_db_item(item_id: NewsItemID) -> DbNewsItem | None:
    """Return the item with that id, or `None` if not found."""
    return (
        db.session.scalars(
            select(DbNewsItem)
            .filter(DbNewsItem.id == item_id)
            .options(
                db.joinedload(DbNewsItem.channel),
                db.joinedload(DbNewsItem.featured_image_association).joinedload(
                    DbFeaturedNewsImage.image
                ),
                db.joinedload(DbNewsItem.images),
            )
        )
        .unique()
        .one_or_none()
    )


def _get_db_item(item_id: NewsItemID) -> DbNewsItem:
    """Return the item with that id, or raise an exception."""
    db_item = _find_db_item(item_id)

    if db_item is None:
        raise ValueError(f'Unknown news item ID "{item_id}".')

    return db_item


def find_rendered_item_by_slug(
    channel_ids: set[NewsChannelID], slug: str, *, published_only: bool = False
) -> RenderedNewsItem | None:
    """Return the rendered item identified by that slug in one of the
    given channels, or `None` if not found.
    """
    stmt = (
        select(DbNewsItem)
        .filter(DbNewsItem.channel_id.in_(channel_ids))
        .filter_by(slug=slug)
        .options(
            db.joinedload(DbNewsItem.channel),
            db.joinedload(DbNewsItem.current_version_association).joinedload(
                DbCurrentNewsItemVersionAssociation.version
            ),
            db.joinedload(DbNewsItem.featured_image_association).joinedload(
                DbFeaturedNewsImage.image
            ),
            db.joinedload(DbNewsItem.images),
        )
    )

    if published_only:
        stmt = stmt.filter(DbNewsItem.published_at <= datetime.utcnow())

    db_item = db.session.scalars(stmt).unique().one_or_none()

    if db_item is None:
        return None

    item = _db_entity_to_item(db_item)
    return render_html(item)


def get_rendered_items_paginated(
    channel_ids: set[NewsChannelID],
    page: int,
    items_per_page: int,
    *,
    published_only: bool = False,
) -> Pagination:
    """Return the rendered news items to show on the specified page."""
    stmt = _get_items_stmt(channel_ids)

    if published_only:
        now = datetime.utcnow()
        stmt = stmt.filter(DbNewsItem.published_at <= now)

    def item_mapper(db_item: DbNewsItem) -> RenderedNewsItem:
        item = _db_entity_to_item(db_item)
        return render_html(item)

    return paginate(stmt, page, items_per_page, item_mapper=item_mapper)


def get_admin_list_items_paginated(
    channel_ids: set[NewsChannelID], page: int, items_per_page: int
) -> Pagination:
    """Return the news items to show on the specified page."""
    stmt = _get_items_stmt(channel_ids)

    def to_admin_list_item(db_item: DbNewsItem) -> AdminListNewsItem:
        db_version = db_item.current_version

        featured_image = _find_featured_image(db_item)

        return AdminListNewsItem(
            id=db_item.id,
            created_at=db_version.created_at,
            creator=db_version.creator_id,
            slug=db_item.slug,
            title=db_version.title,
            image_total=len(db_item.images),
            featured_image=featured_image,
            published=db_item.published,
        )

    pagination = paginate(
        stmt, page, items_per_page, item_mapper=to_admin_list_item
    )

    user_ids = {item.creator for item in pagination.items}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )
    pagination.items = [
        dataclasses.replace(item, creator=users_by_id[item.creator])
        for item in pagination.items
    ]

    return pagination


def _get_items_stmt(channel_ids: set[NewsChannelID]) -> Select:
    return (
        select(DbNewsItem)
        .filter(DbNewsItem.channel_id.in_(channel_ids))
        .options(
            db.joinedload(DbNewsItem.channel),
            db.joinedload(DbNewsItem.current_version_association).joinedload(
                DbCurrentNewsItemVersionAssociation.version
            ),
            db.joinedload(DbNewsItem.featured_image_association).joinedload(
                DbFeaturedNewsImage.image
            ),
            db.joinedload(DbNewsItem.images),
        )
        .order_by(DbNewsItem.published_at.desc())
    )


def get_headlines_paginated(
    channel_ids: set[NewsChannelID],
    page: int,
    items_per_page: int,
    *,
    published_only: bool = False,
) -> Pagination:
    """Return the headlines to show on the specified page."""
    stmt = (
        select(DbNewsItem)
        .filter(DbNewsItem.channel_id.in_(channel_ids))
        .options(
            db.joinedload(DbNewsItem.current_version_association).joinedload(
                DbCurrentNewsItemVersionAssociation.version
            )
        )
        .order_by(DbNewsItem.published_at.desc())
    )

    if published_only:
        now = datetime.utcnow()
        stmt = stmt.filter(DbNewsItem.published_at <= now)

    return paginate(
        stmt, page, items_per_page, item_mapper=_db_entity_to_headline
    )


def get_recent_headlines(
    channel_ids: frozenset[NewsChannelID] | set[NewsChannelID], limit: int
) -> list[NewsHeadline]:
    """Return the most recent headlines."""
    db_items = (
        db.session.scalars(
            select(DbNewsItem)
            .filter(DbNewsItem.channel_id.in_(channel_ids))
            .options(
                db.joinedload(
                    DbNewsItem.current_version_association
                ).joinedload(DbCurrentNewsItemVersionAssociation.version)
            )
            .filter(DbNewsItem.published_at <= datetime.utcnow())
            .order_by(DbNewsItem.published_at.desc())
            .limit(limit)
        )
        .unique()
        .all()
    )

    return [_db_entity_to_headline(db_item) for db_item in db_items]


def get_recent_teasers(
    channel_ids: frozenset[NewsChannelID] | set[NewsChannelID], limit: int
) -> list[NewsTeaser]:
    """Return the most recent teasers."""
    db_items = (
        db.session.scalars(
            select(DbNewsItem)
            .filter(DbNewsItem.channel_id.in_(channel_ids))
            .options(
                db.joinedload(
                    DbNewsItem.current_version_association
                ).joinedload(DbCurrentNewsItemVersionAssociation.version),
                db.joinedload(DbNewsItem.featured_image_association).joinedload(
                    DbFeaturedNewsImage.image
                ),
            )
            .filter(DbNewsItem.published_at <= datetime.utcnow())
            .order_by(DbNewsItem.published_at.desc())
            .limit(limit)
        )
        .unique()
        .all()
    )

    return [_db_entity_to_teaser(db_item) for db_item in db_items]


def find_latest_headline_before(
    channel_ids: frozenset[NewsChannelID] | set[NewsChannelID],
    published_at: datetime,
) -> NewsHeadline | None:
    """Return the latest published headline before the given publication date."""
    db_item = db.session.execute(
        select(DbNewsItem)
        .filter(DbNewsItem.channel_id.in_(channel_ids))
        .options(
            db.joinedload(DbNewsItem.current_version_association).joinedload(
                DbCurrentNewsItemVersionAssociation.version
            )
        )
        .filter(DbNewsItem.published_at < published_at)
        .order_by(DbNewsItem.published_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if db_item is None:
        return None

    return _db_entity_to_headline(db_item)


def find_oldest_headline_after(
    channel_ids: frozenset[NewsChannelID] | set[NewsChannelID],
    published_at: datetime,
) -> NewsHeadline | None:
    """Return the oldest published headline after the given publication date."""
    db_item = db.session.execute(
        select(DbNewsItem)
        .filter(DbNewsItem.channel_id.in_(channel_ids))
        .options(
            db.joinedload(DbNewsItem.current_version_association).joinedload(
                DbCurrentNewsItemVersionAssociation.version
            )
        )
        .filter(DbNewsItem.published_at > published_at)
        .order_by(DbNewsItem.published_at.asc())
        .limit(1)
    ).scalar_one_or_none()

    if db_item is None:
        return None

    return _db_entity_to_headline(db_item)


def get_item_versions(item_id: NewsItemID) -> Sequence[DbNewsItemVersion]:
    """Return all item versions, sorted from most recent to oldest."""
    return db.session.scalars(
        select(DbNewsItemVersion)
        .filter_by(item_id=item_id)
        .order_by(DbNewsItemVersion.created_at.desc())
    ).all()


def get_current_item_version(item_id: NewsItemID) -> DbNewsItemVersion:
    """Return the item's current version."""
    db_item = _get_db_item(item_id)

    return db_item.current_version


def find_item_version(
    version_id: NewsItemVersionID,
) -> DbNewsItemVersion | None:
    """Return the item version with that ID, or `None` if not found."""
    return db.session.get(DbNewsItemVersion, version_id)


def has_channel_items(channel_id: NewsChannelID) -> bool:
    """Return `True` if the channel contains items."""
    return (
        db.session.scalar(
            select(
                select(DbNewsItem)
                .join(DbNewsChannel)
                .filter(DbNewsChannel.id == channel_id)
                .exists()
            )
        )
        or False
    )


def get_item_count_by_channel_id() -> dict[NewsChannelID, int]:
    """Return news item count (including 0) per channel, indexed by
    channel ID.
    """
    channel_ids_and_item_counts = (
        db.session.execute(
            select(DbNewsChannel.id, db.func.count(DbNewsItem.id))
            .outerjoin(DbNewsItem)
            .group_by(DbNewsChannel.id)
        )
        .tuples()
        .all()
    )

    return dict(channel_ids_and_item_counts)


def _db_entity_to_item(db_item: DbNewsItem) -> NewsItem:
    channel = news_channel_service._db_entity_to_channel(db_item.channel)

    images = [
        news_image_service._db_entity_to_image(db_image, channel.id)
        for db_image in db_item.images
    ]

    featured_image = _find_featured_image(db_item)

    return NewsItem(
        id=db_item.id,
        brand_id=db_item.brand_id,
        channel=channel,
        slug=db_item.slug,
        published_at=db_item.published_at,
        published=db_item.published_at is not None,
        title=db_item.current_version.title,
        body=db_item.current_version.body,
        body_format=db_item.current_version.body_format,
        images=images,
        featured_image=featured_image,
    )


def render_html(item: NewsItem) -> RenderedNewsItem:
    """Render item's raw body and featured image to HTML."""
    featured_image_html = (
        _render_featured_image_html(item.id, item.featured_image)
        if item.featured_image
        else None
    )

    return RenderedNewsItem(
        channel=item.channel,
        slug=item.slug,
        published_at=item.published_at,
        published=item.published,
        title=item.title,
        featured_image=item.featured_image,
        featured_image_html=featured_image_html,
        body_html=_render_body_html(item),
    )


def _render_featured_image_html(
    item_id: NewsItemID, image: NewsImage
) -> Result[str, str]:
    result = news_html_service.render_featured_image_html(image)

    if result.is_err():
        # Log, but do not return error.
        log.warning(
            'HTML rendering of featured image for news item %s failed: %s',
            item_id,
            result.unwrap_err(),
        )

    return Ok(result.unwrap())


def _render_body_html(item: NewsItem) -> Result[str, str]:
    result = news_html_service.render_body_html(item)

    if result.is_err():
        # Log, but do not return error.
        log.warning(
            'HTML rendering of body for news item %s failed: %s',
            item.id,
            result.unwrap_err(),
        )

    return result


def _db_entity_to_headline(db_item: DbNewsItem) -> NewsHeadline:
    return NewsHeadline(
        slug=db_item.slug,
        published_at=db_item.published_at,
        published=db_item.published_at is not None,
        title=db_item.current_version.title,
    )


def _db_entity_to_teaser(db_item: DbNewsItem) -> NewsTeaser:
    featured_image = _find_featured_image(db_item)

    return NewsTeaser(
        slug=db_item.slug,
        published_at=db_item.published_at,
        published=db_item.published_at is not None,
        title=db_item.current_version.title,
        featured_image=featured_image,
    )


def is_slug_available(brand_id: BrandID, slug: str) -> bool:
    """Check if the slug is yet unused."""
    return not db.session.scalar(
        select(
            db.exists()
            .where(DbNewsItem.brand_id == brand_id)
            .where(db.func.lower(DbNewsItem.slug) == slug.lower())
        )
    )


def _find_featured_image(db_item: DbNewsItem) -> NewsImage | None:
    db_featured_image = db_item.featured_image
    if not db_featured_image:
        return None

    return news_image_service._db_entity_to_image(
        db_featured_image, db_item.channel_id
    )
