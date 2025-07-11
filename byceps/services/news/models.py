"""
byceps.services.news.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType
from uuid import UUID

from byceps.services.brand.models import BrandID
from byceps.services.user.models.user import User, UserID
from byceps.util.result import Result


NewsChannelID = NewType('NewsChannelID', str)


NewsItemID = NewType('NewsItemID', UUID)


NewsItemVersionID = NewType('NewsItemVersionID', UUID)


NewsImageID = NewType('NewsImageID', UUID)


BodyFormat = Enum('BodyFormat', ['html', 'markdown'])


@dataclass(frozen=True)
class PublicationStatus:
    pass


@dataclass(frozen=True)
class PublicationStatusDraft(PublicationStatus):
    pass


@dataclass(frozen=True)
class PublicationStatusScheduledForPublication(PublicationStatus):
    pass


@dataclass(frozen=True)
class PublicationStatusPublished(PublicationStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class NewsChannel:
    id: NewsChannelID
    brand_id: BrandID
    # Should be `SiteID` instead of `str`,
    # but circular imports prevent this.
    announcement_site_id: str | None
    archived: bool


@dataclass(frozen=True, kw_only=True)
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


@dataclass(frozen=True, kw_only=True)
class NewsItem:
    id: NewsItemID
    brand_id: BrandID
    channel: NewsChannel
    slug: str
    published_at: datetime | None
    published: bool
    title: str
    body: str
    body_format: BodyFormat
    images: list[NewsImage]
    featured_image: NewsImage | None

    @property
    def publication_status(self) -> PublicationStatus:
        if self.published_at is None:
            return PublicationStatusDraft()
        elif self.published_at > datetime.utcnow():
            return PublicationStatusScheduledForPublication()
        else:
            return PublicationStatusPublished()

    @property
    def publication_status_name(self) -> str:
        match self.publication_status:
            case PublicationStatusDraft():
                return 'draft'
            case PublicationStatusScheduledForPublication():
                return 'scheduled_for_publication'
            case PublicationStatusPublished():
                return 'published'
            case _:
                raise ValueError('unknown publication status')


@dataclass(frozen=True, kw_only=True)
class RenderedNewsItem:
    channel: NewsChannel
    slug: str
    published_at: datetime | None
    published: bool
    title: str
    featured_image: NewsImage | None
    featured_image_html: Result[str, str] | None
    body_html: Result[str, str]


@dataclass(frozen=True, kw_only=True)
class NewsHeadline:
    slug: str
    published_at: datetime | None
    published: bool
    title: str


@dataclass(frozen=True, kw_only=True)
class NewsTeaser(NewsHeadline):
    featured_image: NewsImage | None


@dataclass(frozen=True, kw_only=True)
class AdminListNewsItem:
    id: NewsItemID
    created_at: datetime
    creator: User
    slug: str
    title: str
    image_total: int
    featured_image: NewsImage | None
    published: bool
