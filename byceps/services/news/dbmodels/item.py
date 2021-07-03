"""
byceps.services.news.dbmodels.item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy

from ....database import BaseQuery, db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ...user.dbmodels.user import User

from ..transfer.models import ChannelID, ItemID

from .channel import Channel


class ItemQuery(BaseQuery):

    def for_channels(self, channel_ids: set[ChannelID]) -> BaseQuery:
        if not channel_ids:
            raise ValueError('No channel IDs given')

        return self.filter(Item.channel_id.in_(channel_ids))

    def with_channel(self) -> BaseQuery:
        return self.options(
            db.joinedload(Item.channel),
        )

    def with_images(self) -> BaseQuery:
        return self.options(
            db.joinedload(Item.images),
        )

    def published(self) -> BaseQuery:
        """Return items that have been published and are public at this time.

        This excludes items that have been pre-published for a time that
        is still in the future.
        """
        return self.filter(Item.published_at <= datetime.utcnow())

    def with_current_version(self) -> BaseQuery:
        return self.options(
            db.joinedload(Item.current_version_association)
                .joinedload(CurrentVersionAssociation.version),
        )


class Item(db.Model):
    """A news item.

    Each one is expected to have at least one version (the initial one).
    """

    __tablename__ = 'news_items'
    query_class = ItemQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    channel_id = db.Column(db.UnicodeText, db.ForeignKey('news_channels.id'), index=True, nullable=False)
    channel = db.relationship(Channel)
    slug = db.Column(db.UnicodeText, unique=True, index=True, nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    current_version = association_proxy('current_version_association', 'version')

    def __init__(self, channel_id: ChannelID, slug: str) -> None:
        self.channel_id = channel_id
        self.slug = slug

    @property
    def title(self) -> str:
        return self.current_version.title

    @property
    def published(self) -> bool:
        return self.published_at is not None

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('channel', self.channel_id) \
            .add_with_lookup('slug') \
            .add_with_lookup('published_at') \
            .build()


class ItemVersionQuery(BaseQuery):

    def for_item(self, item_id: ItemID) -> BaseQuery:
        return self.filter_by(item_id=item_id)


class ItemVersion(db.Model):
    """A snapshot of a news item at a certain time."""

    __tablename__ = 'news_item_versions'
    query_class = ItemVersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    item_id = db.Column(db.Uuid, db.ForeignKey('news_items.id'), index=True, nullable=False)
    item = db.relationship(Item)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User)
    title = db.Column(db.UnicodeText, nullable=False)
    body = db.Column(db.UnicodeText, nullable=False)
    image_url_path = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self, item: Item, creator_id: UserID, title: str, body: str
    ) -> None:
        self.item = item
        self.creator_id = creator_id
        self.title = title
        self.body = body

    @property
    def is_current(self) -> bool:
        """Return `True` if this version is the current version of the
        item it belongs to.
        """
        return self.id == self.item.current_version.id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('item') \
            .add_with_lookup('created_at') \
            .build()


class CurrentVersionAssociation(db.Model):
    __tablename__ = 'news_item_current_versions'

    item_id = db.Column(db.Uuid, db.ForeignKey('news_items.id'), primary_key=True)
    item = db.relationship(Item, backref=db.backref('current_version_association', uselist=False))
    version_id = db.Column(db.Uuid, db.ForeignKey('news_item_versions.id'), unique=True, nullable=False)
    version = db.relationship(ItemVersion)

    def __init__(self, item: Item, version: ItemVersion) -> None:
        self.item = item
        self.version = version
