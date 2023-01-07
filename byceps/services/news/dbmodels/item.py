"""
byceps.services.news.dbmodels.item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.ext.associationproxy import association_proxy

from ....database import db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ...user.dbmodels.user import DbUser

from ..transfer.models import BodyFormat, NewsChannelID

from .channel import DbNewsChannel


class DbNewsItem(db.Model):
    """A news item.

    Each one is expected to have at least one version (the initial one).

    News items with a publication date set are considered public unless
    that date is in the future (i.e. those items have been pre-published
    and are awaiting publication).
    """

    __tablename__ = 'news_items'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    channel_id = db.Column(
        db.UnicodeText,
        db.ForeignKey('news_channels.id'),
        index=True,
        nullable=False,
    )
    channel = db.relationship(DbNewsChannel)
    slug = db.Column(db.UnicodeText, unique=True, index=True, nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    current_version = association_proxy(
        'current_version_association', 'version'
    )
    featured_image_id = db.Column(db.Uuid, nullable=True)

    def __init__(self, channel_id: NewsChannelID, slug: str) -> None:
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

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    item_id = db.Column(
        db.Uuid, db.ForeignKey('news_items.id'), index=True, nullable=False
    )
    item = db.relationship(DbNewsItem)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(DbUser)
    title = db.Column(db.UnicodeText, nullable=False)
    body = db.Column(db.UnicodeText, nullable=False)
    _body_format = db.Column('body_format', db.UnicodeText, nullable=False)
    image_url_path = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        item: DbNewsItem,
        creator_id: UserID,
        title: str,
        body: str,
        body_format: BodyFormat,
    ) -> None:
        self.item = item
        self.creator_id = creator_id
        self.title = title
        self.body = body
        self.body_format = body_format

    @hybrid_property
    def body_format(self) -> BodyFormat:
        return BodyFormat[self._body_format]

    @body_format.setter
    def body_format(self, body_format: BodyFormat) -> None:
        assert body_format is not None
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

    item_id = db.Column(
        db.Uuid, db.ForeignKey('news_items.id'), primary_key=True
    )
    item = db.relationship(
        DbNewsItem,
        backref=db.backref('current_version_association', uselist=False),
    )
    version_id = db.Column(
        db.Uuid,
        db.ForeignKey('news_item_versions.id'),
        unique=True,
        nullable=False,
    )
    version = db.relationship(DbNewsItemVersion)

    def __init__(self, item: DbNewsItem, version: DbNewsItemVersion) -> None:
        self.item = item
        self.version = version
