"""
byceps.services.news.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType, Optional
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
    announcement_site_id: Optional[str]
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
    alt_text: Optional[str]
    caption: Optional[str]
    attribution: Optional[str]


@dataclass(frozen=True)
class NewsItem:
    id: NewsItemID
    channel: NewsChannel
    slug: str
    published_at: Optional[datetime]
    published: bool
    title: str
    body: str
    body_format: BodyFormat
    image_url_path: Optional[str]
    images: list[NewsImage]
    featured_image_id: Optional[NewsImageID]


@dataclass(frozen=True)
class NewsHeadline:
    slug: str
    published_at: Optional[datetime]
    published: bool
    title: str
