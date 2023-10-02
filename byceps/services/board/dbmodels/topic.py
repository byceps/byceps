"""
byceps.services.board.dbmodels.topic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.board.models import BoardCategoryID, TopicID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .category import DbBoardCategory


class DbTopic(db.Model):
    """A topic."""

    __tablename__ = 'board_topics'

    id: Mapped[TopicID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
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
    last_updated_at: Mapped[Optional[datetime]] = mapped_column(  # noqa: UP007
        default=datetime.utcnow
    )
    last_updated_by_id: Mapped[Optional[UserID]] = mapped_column(  # noqa: UP007
        db.Uuid, db.ForeignKey('users.id')
    )
    last_updated_by: Mapped[Optional[DbUser]] = relationship(  # noqa: UP007
        DbUser, foreign_keys=[last_updated_by_id]
    )
    hidden: Mapped[bool] = mapped_column(default=False)
    hidden_at: Mapped[Optional[datetime]]  # noqa: UP007
    hidden_by_id: Mapped[Optional[UserID]] = mapped_column(  # noqa: UP007
        db.Uuid, db.ForeignKey('users.id')
    )
    hidden_by: Mapped[Optional[DbUser]] = relationship(  # noqa: UP007
        DbUser, foreign_keys=[hidden_by_id]
    )
    locked: Mapped[bool] = mapped_column(default=False)
    locked_at: Mapped[Optional[datetime]]  # noqa: UP007
    locked_by_id: Mapped[Optional[UserID]] = mapped_column(  # noqa: UP007
        db.Uuid, db.ForeignKey('users.id')
    )
    locked_by: Mapped[Optional[DbUser]] = relationship(  # noqa: UP007
        DbUser, foreign_keys=[locked_by_id]
    )
    pinned: Mapped[bool] = mapped_column(default=False)
    pinned_at: Mapped[Optional[datetime]]  # noqa: UP007
    pinned_by_id: Mapped[Optional[UserID]] = mapped_column(  # noqa: UP007
        db.Uuid, db.ForeignKey('users.id')
    )
    pinned_by: Mapped[Optional[DbUser]] = relationship(  # noqa: UP007
        DbUser, foreign_keys=[pinned_by_id]
    )
    initial_posting = association_proxy(
        'initial_topic_posting_association', 'posting'
    )
    posting_limited_to_moderators: Mapped[bool] = mapped_column(default=False)
    muted: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self, category_id: BoardCategoryID, creator_id: UserID, title: str
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
        builder = (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('category', self.category.title)
            .add_with_lookup('title')
        )

        if self.hidden_by:
            builder.add_custom(f'hidden by {self.hidden_by.screen_name}')

        if self.locked_by:
            builder.add_custom(f'locked by {self.locked_by.screen_name}')

        if self.pinned_by:
            builder.add_custom(f'pinned by {self.pinned_by.screen_name}')

        return builder.build()
