"""
byceps.services.board.dbmodels.board_access_grant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.board.models import BoardID
from byceps.services.user.models import UserID


BoardAccessGrantID = NewType('BoardAccessGrantID', UUID)


class DbBoardAccessGrant(db.Model):
    """Access to a specific board granted to a user."""

    __tablename__ = 'board_access_grants'

    id: Mapped[BoardAccessGrantID] = mapped_column(db.Uuid, primary_key=True)
    board_id: Mapped[BoardID] = mapped_column(
        db.UnicodeText, db.ForeignKey('boards.id'), index=True
    )
    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    created_at: Mapped[datetime]

    def __init__(
        self,
        grant_id: BoardAccessGrantID,
        board_id: BoardID,
        user_id: UserID,
        created_at: datetime,
    ) -> None:
        self.id = grant_id
        self.board_id = board_id
        self.user_id = user_id
        self.created_at = created_at
