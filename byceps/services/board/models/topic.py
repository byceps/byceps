"""
byceps.services.board.models.topic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from flask import url_for
from sqlalchemy.ext.associationproxy import association_proxy

from ....blueprints.board.authorization import BoardPermission, \
    BoardTopicPermission
from ....database import BaseQuery, db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ...user.models.user import User

from .category import Category, CategoryID


TopicID = NewType('TopicID', UUID)


class TopicQuery(BaseQuery):

    def for_category(self, category_id: CategoryID) -> BaseQuery:
        return self.filter_by(category_id=category_id)

    def only_visible_for_user(self, user: User) -> BaseQuery:
        """Only return topics the user may see."""
        if not user.has_permission(BoardPermission.view_hidden):
            return self.without_hidden()

        return self

    def without_hidden(self) -> BaseQuery:
        """Only return topics every user may see."""
        return self.filter(Topic.hidden == False)


class Topic(db.Model):
    """A topic."""
    __tablename__ = 'board_topics'
    query_class = TopicQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    category_id = db.Column(db.Uuid, db.ForeignKey('board_categories.id'), index=True, nullable=False)
    category = db.relationship(Category)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User, foreign_keys=[creator_id])
    title = db.Column(db.Unicode(80), nullable=False)
    posting_count = db.Column(db.Integer, default=0, nullable=False)
    last_updated_at = db.Column(db.DateTime, default=datetime.now)
    last_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_updated_by = db.relationship(User, foreign_keys=[last_updated_by_id])
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    hidden_at = db.Column(db.DateTime)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(User, foreign_keys=[hidden_by_id])
    locked = db.Column(db.Boolean, default=False, nullable=False)
    locked_at = db.Column(db.DateTime)
    locked_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    locked_by = db.relationship(User, foreign_keys=[locked_by_id])
    pinned = db.Column(db.Boolean, default=False, nullable=False)
    pinned_at = db.Column(db.DateTime)
    pinned_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    pinned_by = db.relationship(User, foreign_keys=[pinned_by_id])
    initial_posting = association_proxy('initial_topic_posting_association', 'posting')

    def __init__(self, category_id: CategoryID, creator_id: UserID, title: str
                ) -> None:
        self.category_id = category_id
        self.creator_id = creator_id
        self.title = title

    def may_be_updated_by_user(self, user: User) -> bool:
        return (
            (
                not self.locked
                    and user == self.creator
                    and user.has_permission(BoardTopicPermission.update)
            )
            or user.has_permission(BoardPermission.update_of_others)
        )

    @property
    def reply_count(self) -> int:
        return self.posting_count - 1

    def count_pages(self, postings_per_page: int) -> int:
        """Return the number of pages this topic spans."""
        full_page_count, remaining_postings = divmod(self.posting_count,
                                                     postings_per_page)
        if remaining_postings > 0:
            return full_page_count + 1
        else:
            return full_page_count

    @property
    def anchor(self) -> str:
        """Return the URL anchor for this topic."""
        return 'topic-{}'.format(self.id)

    @property
    def external_url(self) -> str:
        """Return the absolute URL of this topic."""
        return url_for('board.topic_view', topic_id=self.id, _external=True)

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('category', self.category.title) \
            .add('creator', self.creator.screen_name) \
            .add_with_lookup('title')

        if self.hidden:
            builder.add_custom('hidden by {}'.format(self.hidden_by.screen_name))

        if self.locked:
            builder.add_custom('locked by {}'.format(self.locked_by.screen_name))

        if self.pinned:
            builder.add_custom('pinned by {}'.format(self.pinned_by.screen_name))

        return builder.build()
