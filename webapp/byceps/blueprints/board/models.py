# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import g

from ...database import BaseQuery, db
from ...util.instances import ReprBuilder

from ..brand.models import Brand
from ..user.models import User


class CategoryQuery(BaseQuery):

    def for_current_brand(self):
        return self.filter_by(brand=g.party.brand)


class Category(db.Model):
    """A category for topics."""
    __tablename__ = 'board_categories'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'title'),
        db.UniqueConstraint('brand_id', 'position'),
    )
    query_class = CategoryQuery

    id = db.Column(db.Unicode(40), primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    brand = db.relationship(Brand)
    position = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)
    topic_count = db.Column(db.Integer, default=0, nullable=False)
    posting_count = db.Column(db.Integer, default=0, nullable=False)
    latest_posting_updated_at = db.Column(db.DateTime)
    latest_posting_author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    latest_posting_author = db.relationship(User)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('brand') \
            .add_with_lookup('title') \
            .build()
