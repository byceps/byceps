"""
byceps.services.board.dbmodels.last_category_view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.board.models import BoardCategoryID
from byceps.typing import UserID
from byceps.util.instances import ReprBuilder

from .category import DbBoardCategory


class DbLastCategoryView(db.Model):
    """The last time a user looked into specific category."""

    __tablename__ = 'board_categories_lastviews'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    category_id: Mapped[BoardCategoryID] = mapped_column(
        db.Uuid, db.ForeignKey('board_categories.id'), primary_key=True
    )
    category: Mapped[DbBoardCategory] = relationship(DbBoardCategory)
    occurred_at: Mapped[datetime]

    def __init__(
        self,
        user_id: UserID,
        category_id: BoardCategoryID,
        occurred_at: datetime,
    ) -> None:
        self.user_id = user_id
        self.category_id = category_id
        self.occurred_at = occurred_at

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('user_id')
            .add('category', self.category.title)
            .add_with_lookup('occurred_at')
            .build()
        )
