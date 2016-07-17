# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.models.category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from sqlalchemy.ext.orderinglist import ordering_list

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder

from ...brand.models import Brand
from ...user.models.user import User


class CategoryQuery(BaseQuery):

    def for_brand(self, brand):
        return self.filter_by(brand=brand)


class Category(db.Model):
    """A category for topics."""
    __tablename__ = 'board_categories'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'slug'),
        db.UniqueConstraint('brand_id', 'title'),
    )
    query_class = CategoryQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    slug = db.Column(db.Unicode(40), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)
    description = db.Column(db.Unicode(80))
    topic_count = db.Column(db.Integer, default=0, nullable=False)
    posting_count = db.Column(db.Integer, default=0, nullable=False)
    last_posting_updated_at = db.Column(db.DateTime)
    last_posting_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_posting_updated_by = db.relationship(User)

    brand = db.relationship(Brand,
                            backref=db.backref('board_categories',
                                               order_by=position,
                                               collection_class=ordering_list('position', count_from=1)))

    def __init__(self, brand, slug, title, description):
        self.brand = brand
        self.slug = slug
        self.title = title
        self.description = description

    def contains_unseen_postings(self, user):
        """Return `True` if the category contains postings created after
        the last time the user viewed it.
        """
        # Don't display as new to a guest.
        if user.is_anonymous:
            return False

        if self.last_posting_updated_at is None:
            return False

        last_view = LastCategoryView.find(user, self)

        if last_view is None:
            return True

        return self.last_posting_updated_at > last_view.occured_at

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('brand') \
            .add_with_lookup('slug') \
            .add_with_lookup('title') \
            .build()


class LastCategoryView(db.Model):
    """The last time a user looked into specific category."""
    __tablename__ = 'board_categories_lastviews'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, foreign_keys=[user_id])
    category_id = db.Column(db.Uuid, db.ForeignKey('board_categories.id'), primary_key=True)
    category = db.relationship(Category)
    occured_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user, category):
        self.user = user
        self.category = category

    @classmethod
    def find(cls, user, category):
        if user.is_anonymous:
            return

        return cls.query.filter_by(user=user, category=category).first()

    def __repr__(self):
        return ReprBuilder(self) \
            .add('user', self.user.screen_name) \
            .add('category', self.category.title) \
            .add_with_lookup('occured_at') \
            .build()
