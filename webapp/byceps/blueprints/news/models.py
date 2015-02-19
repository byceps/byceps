# -*- coding: utf-8 -*-

"""
byceps.blueprints.news.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import datetime

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..brand.models import Brand
from ..snippet.models import Snippet


class ItemQuery(BaseQuery):

    def for_brand(self, brand):
        return self.filter_by(brand_id=brand.id)


class Item(db.Model):
    """A news item."""
    __tablename__ = 'news_items'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'slug'),
        db.UniqueConstraint('brand_id', 'snippet_id'),
    )
    query_class = ItemQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)
    brand = db.relationship(Brand)
    slug = db.Column(db.Unicode(40), index=True, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)

    @property
    def title(self):
        return self.snippet.get_latest_version().title

    @property
    def body(self):
        return self.snippet.get_latest_version().body

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .add_with_lookup('slug') \
            .add_with_lookup('published_at') \
            .build()
