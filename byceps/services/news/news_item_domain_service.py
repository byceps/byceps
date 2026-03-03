"""
byceps.services.news.news_item_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime

from byceps.services.site.models import Site
from byceps.services.user.models import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .events import NewsItemPublishedEvent
from .models import (
    BodyFormat,
    NewsChannel,
    NewsItem,
    NewsItemID,
    RenderedNewsItem,
)


def create_item(
    channel: NewsChannel,
    slug: str,
    title: str,
    body: str,
    body_format: BodyFormat,
) -> Result[NewsItem, str]:
    """Create a news item."""
    if channel.archived:
        return Err('Channel is archived.')

    item_id = NewsItemID(generate_uuid7())
    created_at = datetime.utcnow()

    item = NewsItem(
        id=item_id,
        created_at=created_at,
        brand_id=channel.brand_id,
        channel=channel,
        slug=slug,
        published_at=None,
        published=False,
        title=title,
        body=body,
        body_format=body_format,
        images=[],
        featured_image=None,
    )

    return Ok(item)


def publish_item(
    item: NewsItem,
    *,
    publish_at: datetime | None = None,
    announcement_site: Site | None = None,
    initiator: User | None = None,
) -> Result[tuple[NewsItem, NewsItemPublishedEvent], str]:
    """Publish a news item."""
    if item.published:
        return Err('News item has already been published')

    now = datetime.utcnow()

    if publish_at is None:
        publish_at = now

    published_item = dataclasses.replace(item, published_at=publish_at)

    if announcement_site is not None:
        external_url = (
            f'https://{announcement_site.server_name}/news/{item.slug}'
        )
    else:
        external_url = None

    event = NewsItemPublishedEvent(
        occurred_at=now,
        initiator=initiator,
        item_id=item.id,
        channel_id=item.channel.id,
        published_at=publish_at,
        title=item.title,
        external_url=external_url,
    )

    return Ok((published_item, event))


def create_rendered_item(
    item: NewsItem,
    featured_image_html: Result[str, str] | None,
    body_html: Result[str, str],
) -> RenderedNewsItem:
    """Create rendered news item."""
    return RenderedNewsItem(
        channel=item.channel,
        slug=item.slug,
        published_at=item.published_at,
        published=item.published,
        title=item.title,
        featured_image=item.featured_image,
        featured_image_html=featured_image_html,
        body_html=body_html,
    )
