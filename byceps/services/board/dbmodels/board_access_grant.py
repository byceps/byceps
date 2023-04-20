"""
byceps.services.board.dbmodels.board_access_grant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import NewType

from byceps.database import db, generate_uuid7
from byceps.services.board.models import BoardID
from byceps.typing import UserID
from byceps.util.instances import ReprBuilder


BoardAccessGrantID = NewType('BoardAccessGrantID', str)


class DbBoardAccessGrant(db.Model):
    """Access to a specific board granted to a user."""

    __tablename__ = 'board_access_grants'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    board_id = db.Column(
        db.UnicodeText, db.ForeignKey('boards.id'), index=True, nullable=False
    )
    user_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, board_id: BoardID, user_id: UserID) -> None:
        self.board_id = board_id
        self.user_id = user_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('board_id')
            .add_with_lookup('user_id')
            .build()
        )
