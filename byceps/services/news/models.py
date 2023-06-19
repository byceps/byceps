"""
byceps.services.news.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType
from uuid import UUID

from byceps.typing import BrandID, UserID


NewsChannelID = NewType('NewsChannelID', str)


NewsItemID = NewType('NewsItemID', UUID)


NewsItemVersionID = NewType('NewsItemVersionID', UUID)


NewsImageID = NewType('NewsImageID', UUID)


BodyFormat = Enum('BodyFormat', ['html', 'markdown'])


@dataclass(frozen=True)
class NewsChannel:
    id: NewsChannelID
    brand_id: BrandID
    # Should be `SiteID` instead of `str`,
    # but circular imports prevent this.
    announcement_site_id: str | None
    archived: bool


@dataclass(frozen=True)
class NewsImage:
    id: NewsImageID
    created_at: datetime
    creator_id: UserID
    item_id: NewsItemID
    number: int
    filename: str
    url_path: str
    alt_text: str | None
    caption: str | None
    attribution: str | None


@dataclass(frozen=True)
class NewsItemHtml:
    body: str
    featured_image: str | None


@dataclass(frozen=True)
class NewsItem:
    id: NewsItemID
    channel: NewsChannel
    slug: str
    published_at: datetime | None
    published: bool
    title: str
    body: str
    body_format: BodyFormat
    image_url_path: str | None
    images: list[NewsImage]
    featured_image_id: NewsImageID | None
    featured_image_html: str | None


@dataclass(frozen=True)
class RenderedNewsItem:
    channel: NewsChannel
    slug: str
    published_at: datetime | None
    published: bool
    title: str
    featured_image_html: str | None
    body_html: str | None


@dataclass(frozen=True)
class NewsHeadline:
    slug: str
    published_at: datetime | None
    published: bool
    title: str
