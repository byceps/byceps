"""
byceps.services.news.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType, Optional
from uuid import UUID

from flask import url_for
from sqlalchemy.ext.associationproxy import association_proxy

from ...database import BaseQuery, db, generate_uuid
from ...typing import BrandID, UserID
from ...util.instances import ReprBuilder
from ...util.templating import load_template

from ..brand.models import Brand
from ..user.models.user import User


ItemID = NewType('ItemID', UUID)


class ItemQuery(BaseQuery):

    def for_brand_id(self, brand_id: BrandID) -> BaseQuery:
        return self.filter_by(brand_id=brand_id)

    def with_current_version(self) -> BaseQuery:
        return self.options(
            db.joinedload('current_version_association').joinedload('version'),
        )


class Item(db.Model):
    """A news item.

    Each one is expected to have at least one version (the initial one).
    """
    __tablename__ = 'news_items'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'slug'),
    )
    query_class = ItemQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)
    brand = db.relationship(Brand)
    slug = db.Column(db.Unicode(80), index=True, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    current_version = association_proxy('current_version_association', 'version')

    def __init__(self, brand_id: BrandID, slug: str) -> None:
        self.brand_id = brand_id
        self.slug = slug

    @property
    def title(self) -> str:
        return self.current_version.title

    def render_body(self) -> str:
        template = load_template(self.current_version.body)
        return template.render(url_for=url_for)

    @property
    def external_url(self) -> str:
        return url_for('news.view', slug=self.slug, _external=True)

    @property
    def image_url(self) -> Optional[str]:
        url_path = self.current_version.image_url_path

        if not url_path:
            return None

        filename = 'news/{}'.format(url_path)
        return url_for('brand_file',
                       filename=filename,
                       _method='GET',
                       _external=True)

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .add_with_lookup('slug') \
            .add_with_lookup('published_at') \
            .build()


class ItemVersionQuery(BaseQuery):

    def for_item(self, item: Item) -> BaseQuery:
        return self.filter_by(item=item)


class ItemVersion(db.Model):
    """A snapshot of a news item at a certain time."""
    __tablename__ = 'news_item_versions'
    query_class = ItemVersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    item_id = db.Column(db.Uuid, db.ForeignKey('news_items.id'), index=True, nullable=False)
    item = db.relationship(Item)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User)
    title = db.Column(db.Unicode(80))
    body = db.Column(db.UnicodeText, nullable=False)
    image_url_path = db.Column(db.Unicode(80), nullable=True)

    def __init__(self, item: Item, creator_id: UserID, title: str, body: str
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
