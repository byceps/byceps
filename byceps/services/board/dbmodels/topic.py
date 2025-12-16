"""
byceps.services.board.dbmodels.topic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.board.models import BoardCategoryID, TopicID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder

from .category import DbBoardCategory


class DbTopic(db.Model):
    """A topic."""

    __tablename__ = 'board_topics'

    id: Mapped[TopicID] = mapped_column(db.Uuid, primary_key=True)
    category_id: Mapped[BoardCategoryID] = mapped_column(
        db.Uuid,
        db.ForeignKey('board_categories.id'),
        index=True,
        nullable=False,
    )
    category: Mapped[DbBoardCategory] = relationship(DbBoardCategory)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow
    )
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    title: Mapped[str] = mapped_column(db.UnicodeText)
    posting_count: Mapped[int] = mapped_column(default=0)
    last_updated_at: Mapped[datetime | None] = mapped_column(
        default=datetime.utcnow
    )
    last_updated_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    last_updated_by: Mapped[DbUser | None] = relationship(
        DbUser, foreign_keys=[last_updated_by_id]
    )
    hidden: Mapped[bool] = mapped_column(default=False)
    hidden_at: Mapped[datetime | None]
    hidden_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    hidden_by: Mapped[DbUser | None] = relationship(
        DbUser, foreign_keys=[hidden_by_id]
    )
    locked: Mapped[bool] = mapped_column(default=False)
    locked_at: Mapped[datetime | None]
    locked_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    locked_by: Mapped[DbUser | None] = relationship(
        DbUser, foreign_keys=[locked_by_id]
    )
    pinned: Mapped[bool] = mapped_column(default=False)
    pinned_at: Mapped[datetime | None]
    pinned_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    pinned_by: Mapped[DbUser | None] = relationship(
        DbUser, foreign_keys=[pinned_by_id]
    )
    initial_posting = association_proxy(
        'initial_topic_posting_association', 'posting'
    )
    posting_limited_to_moderators: Mapped[bool] = mapped_column(default=False)
    muted: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        topic_id: TopicID,
        category_id: BoardCategoryID,
        creator_id: UserID,
        title: str,
    ) -> None:
        self.id = topic_id
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
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('category', self.category.title)
            .add_with_lookup('title')
            .build()
        )


class DbLastTopicView(db.Model):
    """The last time a user looked into specific topic."""

    __tablename__ = 'board_topics_lastviews'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    topic_id: Mapped[TopicID] = mapped_column(
        db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True
    )
    topic: Mapped[DbTopic] = relationship(DbTopic)
    occurred_at: Mapped[datetime]

    def __init__(
        self, user_id: UserID, topic_id: TopicID, occurred_at: datetime
    ) -> None:
        self.user_id = user_id
        self.topic_id = topic_id
        self.occurred_at = occurred_at

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('user_id')
            .add('topic', self.topic.title)
            .add_with_lookup('occurred_at')
            .build()
        )
