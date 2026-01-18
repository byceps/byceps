"""
byceps.services.news.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.brand.models import BrandID
from byceps.services.news.models import (
    BodyFormat,
    NewsChannelID,
    NewsImageID,
    NewsItemID,
    NewsItemVersionID,
)
from byceps.services.site.models import SiteID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder


class DbNewsChannel(db.Model):
    """A channel to which news items can be published."""

    __tablename__ = 'news_channels'

    id: Mapped[NewsChannelID] = mapped_column(db.UnicodeText, primary_key=True)
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), index=True
    )
    announcement_site_id: Mapped[SiteID | None] = mapped_column(
        db.UnicodeText, db.ForeignKey('sites.id')
    )
    archived: Mapped[bool]

    def __init__(
        self,
        channel_id: NewsChannelID,
        brand_id: BrandID,
        announcement_site_id: SiteID | None,
        archived: bool,
    ) -> None:
        self.id = channel_id
        self.brand_id = brand_id
        self.announcement_site_id = announcement_site_id
        self.archived = archived

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('brand', self.brand_id)
            .build()
        )


class DbNewsItem(db.Model):
    """A news item.

    Each one is expected to have at least one version (the initial one).

    News items with a publication date set are considered public unless
    that date is in the future (i.e. those items have been pre-published
    and are awaiting publication).
    """

    __tablename__ = 'news_items'
    __table_args__ = (db.UniqueConstraint('brand_id', 'slug'),)

    id: Mapped[NewsItemID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id')
    )
    channel_id: Mapped[NewsChannelID] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('news_channels.id'),
        index=True,
    )
    channel: Mapped[DbNewsChannel] = relationship(DbNewsChannel)
    slug: Mapped[str] = mapped_column(db.UnicodeText)
    published_at: Mapped[datetime | None]
    current_version = association_proxy(
        'current_version_association', 'version'
    )
    featured_image = association_proxy('featured_image_association', 'image')

    def __init__(
        self,
        item_id: NewsItemID,
        created_at: datetime,
        brand_id: BrandID,
        channel_id: NewsChannelID,
        slug: str,
    ) -> None:
        self.id = item_id
        self.created_at = created_at
        self.brand_id = brand_id
        self.channel_id = channel_id
        self.slug = slug

    @property
    def title(self) -> str:
        return self.current_version.title

    @property
    def published(self) -> bool:
        return self.published_at is not None

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('channel', self.channel_id)
            .add_with_lookup('slug')
            .add_with_lookup('published_at')
            .build()
        )


class DbNewsItemVersion(db.Model):
    """A snapshot of a news item at a certain time."""

    __tablename__ = 'news_item_versions'

    id: Mapped[NewsItemVersionID] = mapped_column(db.Uuid, primary_key=True)
    item_id: Mapped[NewsItemID] = mapped_column(
        db.Uuid, db.ForeignKey('news_items.id'), index=True
    )
    item: Mapped[DbNewsItem] = relationship(DbNewsItem)
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    creator: Mapped[DbUser] = relationship(DbUser)
    title: Mapped[str] = mapped_column(db.UnicodeText)
    body: Mapped[str] = mapped_column(db.UnicodeText)
    _body_format: Mapped[str] = mapped_column('body_format', db.UnicodeText)

    def __init__(
        self,
        version_id: NewsItemVersionID,
        item: DbNewsItem,
        created_at: datetime,
        creator_id: UserID,
        title: str,
        body: str,
        body_format: BodyFormat,
    ) -> None:
        self.id = version_id
        self.item = item
        self.created_at = created_at
        self.creator_id = creator_id
        self.title = title
        self.body = body
        self.body_format = body_format

    @hybrid_property
    def body_format(self) -> BodyFormat:
        return BodyFormat[self._body_format]

    @body_format.setter
    def body_format(self, body_format: BodyFormat) -> None:
        self._body_format = body_format.name

    @property
    def is_current(self) -> bool:
        """Return `True` if this version is the current version of the
        item it belongs to.
        """
        return self.id == self.item.current_version.id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('item')
            .add_with_lookup('created_at')
            .build()
        )


class DbCurrentNewsItemVersionAssociation(db.Model):
    __tablename__ = 'news_item_current_versions'

    item_id: Mapped[NewsItemID] = mapped_column(
        db.Uuid, db.ForeignKey('news_items.id'), primary_key=True
    )
    item: Mapped[DbNewsItem] = relationship(
        DbNewsItem,
        backref=db.backref('current_version_association', uselist=False),
    )
    version_id: Mapped[NewsItemVersionID] = mapped_column(
        db.Uuid,
        db.ForeignKey('news_item_versions.id'),
        unique=True,
        nullable=False,
    )
    version: Mapped[DbNewsItemVersion] = relationship(DbNewsItemVersion)

    def __init__(self, item: DbNewsItem, version: DbNewsItemVersion) -> None:
        self.item = item
        self.version = version


class DbNewsImage(db.Model):
    """An image to illustrate a news item."""

    __tablename__ = 'news_images'
    __table_args__ = (db.UniqueConstraint('item_id', 'number'),)

    id: Mapped[NewsImageID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    item_id: Mapped[NewsItemID] = mapped_column(
        db.Uuid, db.ForeignKey('news_items.id'), index=True
    )
    item: Mapped[DbNewsItem] = relationship(DbNewsItem, backref='images')
    number: Mapped[int]
    filename: Mapped[str] = mapped_column(db.UnicodeText)
    alt_text: Mapped[str | None] = mapped_column(db.UnicodeText)
    caption: Mapped[str | None] = mapped_column(db.UnicodeText)
    attribution: Mapped[str | None] = mapped_column(db.UnicodeText)

    def __init__(
        self,
        image_id: NewsImageID,
        created_at: datetime,
        creator_id: UserID,
        item_id: NewsItemID,
        number: int,
        filename: str,
        *,
        alt_text: str | None = None,
        caption: str | None = None,
        attribution: str | None = None,
    ) -> None:
        self.id = image_id
        self.created_at = created_at
        self.creator_id = creator_id
        self.item_id = item_id
        self.number = number
        self.filename = filename
        self.alt_text = alt_text
        self.caption = caption
        self.attribution = attribution

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('item_id')
            .add_with_lookup('number')
            .build()
        )


class DbFeaturedNewsImage(db.Model):
    __tablename__ = 'news_featured_images'

    item_id: Mapped[NewsItemID] = mapped_column(
        db.Uuid, db.ForeignKey('news_items.id'), primary_key=True
    )
    item: Mapped[DbNewsItem] = relationship(
        DbNewsItem,
        backref=db.backref('featured_image_association', uselist=False),
    )
    image_id: Mapped[NewsImageID] = mapped_column(
        db.Uuid, db.ForeignKey('news_images.id'), unique=True
    )
    image: Mapped[DbNewsImage] = relationship(DbNewsImage)

    def __init__(self, item_id: NewsItemID, image_id: NewsImageID) -> None:
        self.item_id = item_id
        self.image_id = image_id
