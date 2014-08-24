# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import g

from ...database import BaseQuery, db, generate_uuid
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

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'))
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


class Topic(db.Model):
    """A topic."""
    __tablename__ = 'board_topics'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    category_id = db.Column(db.Uuid, db.ForeignKey('board_categories.id'))
    category = db.relationship(Category, backref='topics')
    created_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    author = db.relationship(User, foreign_keys=[author_id])
    title = db.Column(db.Unicode(80))
    is_sticky = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    posting_count = db.Column(db.Integer, default=0)
    last_updated_at = db.Column(db.DateTime, default=datetime.now())
    last_author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_author = db.relationship(User, foreign_keys=[last_author_id])

    @property
    def is_new(self):
        return True # TODO

    @property
    def reply_count(self):
        return self.posting_count - 1

    def __repr__(self):
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('category', self.category.title) \
            .add('author', self.author.screen_name) \
            .add_with_lookup('title')

        if self.is_sticky:
            builder.add_custom('sticky')

        if self.is_locked:
            builder.add_custom('locked')

        return builder.build()


class Posting(db.Model):
    """A posting."""
    __tablename__ = 'board_postings'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'))
    topic = db.relationship(Topic, backref='postings')
    created_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    author = db.relationship(User, foreign_keys=[author_id])
    body = db.Column(db.UnicodeText)
    is_blocked = db.Column(db.Boolean, default=False)
    last_edited_at = db.Column(db.DateTime, default=datetime.now())
    last_editor_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_editor = db.relationship(User, foreign_keys=[last_editor_id])
    edit_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('topic', self.topic.title) \
            .add('author', self.author.screen_name)

        if self.is_blocked:
            builder.add_custom('blocked')

        return builder.build()
