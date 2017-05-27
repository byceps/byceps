"""
byceps.services.board.models.category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import UUID
from typing import NewType, Optional

from sqlalchemy.ext.orderinglist import ordering_list

from ....database import BaseQuery, db, generate_uuid
from ....typing import BrandID, UserID
from ....util.instances import ReprBuilder

from ...brand.models import Brand
from ...user.models.user import User


CategoryID = NewType('CategoryID', UUID)


class CategoryQuery(BaseQuery):

    def for_brand_id(self, brand_id: BrandID) -> BaseQuery:
        return self.filter_by(brand_id=brand_id)


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

    def __init__(self, brand_id: BrandID, slug: str, title: str,
                 description: str) -> None:
        self.brand_id = brand_id
        self.slug = slug
        self.title = title
        self.description = description

    def contains_unseen_postings(self, user: User) -> bool:
        """Return `True` if the category contains postings created after
        the last time the user viewed it.
        """
        # Don't display as new to a guest.
        if user.is_anonymous:
            return False

        if self.last_posting_updated_at is None:
            return False

        last_view = LastCategoryView.find(user, self.id)

        if last_view is None:
            return True

        return self.last_posting_updated_at > last_view.occured_at

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
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

    def __init__(self, user_id: UserID, category_id: CategoryID) -> None:
        self.user_id = user_id
        self.category_id = category_id

    @classmethod
    def find(cls, user: User, category_id: CategoryID
            ) -> Optional['LastCategoryView']:
        if user.is_anonymous:
            return None

        return cls.query.filter_by(user=user, category_id=category_id).first()

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('user', self.user.screen_name) \
            .add('category', self.category.title) \
            .add_with_lookup('occured_at') \
            .build()
