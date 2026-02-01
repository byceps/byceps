"""
byceps.services.board.dbmodels.topic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.board.models import BoardCategoryID, TopicID
from byceps.services.user.dbmodels import DbUser
from byceps.services.user.models import UserID

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
    category: Mapped[DbBoardCategory] = relationship()
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    title: Mapped[str] = mapped_column(db.UnicodeText)
    posting_count: Mapped[int] = mapped_column(default=0)
    last_updated_at: Mapped[datetime]
    last_updated_by_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    last_updated_by: Mapped[DbUser] = relationship(
        foreign_keys=[last_updated_by_id]
    )
    hidden: Mapped[bool] = mapped_column(default=False)
    hidden_at: Mapped[datetime | None]
    hidden_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    hidden_by: Mapped[DbUser | None] = relationship(foreign_keys=[hidden_by_id])
    locked: Mapped[bool] = mapped_column(default=False)
    locked_at: Mapped[datetime | None]
    locked_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    locked_by: Mapped[DbUser | None] = relationship(foreign_keys=[locked_by_id])
    pinned: Mapped[bool] = mapped_column(default=False)
    pinned_at: Mapped[datetime | None]
    pinned_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    pinned_by: Mapped[DbUser | None] = relationship(foreign_keys=[pinned_by_id])
    initial_posting = association_proxy(
        'initial_topic_posting_association', 'posting'
    )
    posting_limited_to_moderators: Mapped[bool] = mapped_column(default=False)
    muted: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        topic_id: TopicID,
        category_id: BoardCategoryID,
        created_at: datetime,
        creator_id: UserID,
        title: str,
    ) -> None:
        self.id = topic_id
        self.category_id = category_id
        self.created_at = created_at
        self.creator_id = creator_id
        self.title = title
        self.last_updated_at = created_at
        self.last_updated_by_id = creator_id

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


class DbLastTopicView(db.Model):
    """The last time a user looked into specific topic."""

    __tablename__ = 'board_topics_lastviews'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    topic_id: Mapped[TopicID] = mapped_column(
        db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True
    )
    topic: Mapped[DbTopic] = relationship()
    occurred_at: Mapped[datetime]

    def __init__(
        self, user_id: UserID, topic_id: TopicID, occurred_at: datetime
    ) -> None:
        self.user_id = user_id
        self.topic_id = topic_id
        self.occurred_at = occurred_at
