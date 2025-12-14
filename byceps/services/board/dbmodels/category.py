"""
byceps.services.board.dbmodels.category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.board.models import BoardCategoryID, BoardID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder

from .board import DbBoard


class DbBoardCategory(db.Model):
    """A category for topics."""

    __tablename__ = 'board_categories'
    __table_args__ = (
        db.UniqueConstraint('board_id', 'slug'),
        db.UniqueConstraint('board_id', 'title'),
    )

    id: Mapped[BoardCategoryID] = mapped_column(db.Uuid, primary_key=True)
    board_id: Mapped[BoardID] = mapped_column(
        db.UnicodeText, db.ForeignKey('boards.id'), index=True
    )
    position: Mapped[int] = mapped_column(db.Integer)
    slug: Mapped[str] = mapped_column(db.UnicodeText)
    title: Mapped[str] = mapped_column(db.UnicodeText)
    description: Mapped[str | None] = mapped_column(db.UnicodeText)
    topic_count: Mapped[int] = mapped_column(default=0)
    posting_count: Mapped[int] = mapped_column(default=0)
    last_posting_updated_at: Mapped[datetime | None]
    last_posting_updated_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    last_posting_updated_by: Mapped[DbUser | None] = relationship(DbUser)
    hidden: Mapped[bool] = mapped_column(default=False)

    board: Mapped[DbBoard] = relationship(
        DbBoard,
        backref=db.backref(
            'categories',
            order_by=position,
            collection_class=ordering_list('position', count_from=1),
        ),
    )

    def __init__(
        self,
        category_id: BoardCategoryID,
        board_id: BoardID,
        slug: str,
        title: str,
        description: str | None,
    ) -> None:
        self.id = category_id
        self.board_id = board_id
        self.slug = slug
        self.title = title
        self.description = description

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('board', self.board_id)
            .add_with_lookup('slug')
            .add_with_lookup('title')
            .build()
        )
