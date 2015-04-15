# -*- coding: utf-8 -*-

"""
byceps.blueprints.news.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import url_for

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..brand.models import Brand
from ..snippet.models import Snippet
from ..snippet.templating import render_body


class ItemQuery(BaseQuery):

    def for_brand(self, brand):
        return self.filter_by(brand_id=brand.id)

    def with_current_version(self):
        return self.options(
            db.joinedload_all('snippet.current_version_association.version'),
        )


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
    slug = db.Column(db.Unicode(80), index=True, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)

    @property
    def title(self):
        return self.snippet.current_version.title

    def render_body(self):
        return render_body(self.snippet.current_version)

    @property
    def image_url(self):
        url_path = self.snippet.current_version.image_url_path
        if url_path:
            return url_for('content_file', filename=url_path, _external=True)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .add_with_lookup('slug') \
            .add_with_lookup('published_at') \
            .build()
