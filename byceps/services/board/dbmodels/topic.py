"""
byceps.services.board.dbmodels.topic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy

from ....database import db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ...user.dbmodels.user import DbUser

from ..transfer.models import CategoryID

from .category import DbCategory


class DbTopic(db.Model):
    """A topic."""

    __tablename__ = 'board_topics'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    category_id = db.Column(db.Uuid, db.ForeignKey('board_categories.id'), index=True, nullable=False)
    category = db.relationship(DbCategory)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)
    posting_count = db.Column(db.Integer, default=0, nullable=False)
    last_updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_updated_by = db.relationship(DbUser, foreign_keys=[last_updated_by_id])
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    hidden_at = db.Column(db.DateTime)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(DbUser, foreign_keys=[hidden_by_id])
    locked = db.Column(db.Boolean, default=False, nullable=False)
    locked_at = db.Column(db.DateTime)
    locked_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    locked_by = db.relationship(DbUser, foreign_keys=[locked_by_id])
    pinned = db.Column(db.Boolean, default=False, nullable=False)
    pinned_at = db.Column(db.DateTime)
    pinned_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    pinned_by = db.relationship(DbUser, foreign_keys=[pinned_by_id])
    initial_posting = association_proxy('initial_topic_posting_association', 'posting')
    posting_limited_to_moderators = db.Column(db.Boolean, default=False, nullable=False)
    muted = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self, category_id: CategoryID, creator_id: UserID, title: str
    ) -> None:
        self.category_id = category_id
        self.creator_id = creator_id
        self.title = title

    @property
    def reply_count(self) -> int:
        return self.posting_count - 1

    def count_pages(self, postings_per_page: int) -> int:
        """Return the number of pages this topic spans."""
        full_page_count, remaining_postings = divmod(
            self.posting_count, postings_per_page
        )
        if remaining_postings > 0:
            return full_page_count + 1
        else:
            return full_page_count

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('category', self.category.title) \
            .add_with_lookup('title')

        if self.hidden:
            builder.add_custom(f'hidden by {self.hidden_by.screen_name}')

        if self.locked:
            builder.add_custom(f'locked by {self.locked_by.screen_name}')

        if self.pinned:
            builder.add_custom(f'pinned by {self.pinned_by.screen_name}')

        return builder.build()
