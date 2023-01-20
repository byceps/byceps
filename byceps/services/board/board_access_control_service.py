"""
byceps.services.board.board_access_control_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from ...database import db
from ...typing import UserID

from .dbmodels.board import DbBoard
from .dbmodels.board_access_grant import DbBoardAccessGrant, BoardAccessGrantID
from .models import BoardID


def grant_access_to_board(
    board_id: BoardID, user_id: UserID
) -> BoardAccessGrantID:
    """Grant the user access to the board."""
    db_grant = DbBoardAccessGrant(board_id, user_id)

    db.session.add(db_grant)
    db.session.commit()

    return db_grant.id


def revoke_access_to_board(grant_id: BoardAccessGrantID) -> None:
    """Revoke the user's access to the board."""
    db_grant = db.session.get(DbBoardAccessGrant, grant_id)
    if db_grant is None:
        raise ValueError(f"Unknown board grant ID '{grant_id}'")

    db.session.execute(
        delete(DbBoardAccessGrant).where(DbBoardAccessGrant.id == db_grant.id)
    )
    db.session.commit()


def has_user_access_to_board(user_id: UserID, board_id: BoardID) -> bool:
    """Return `True` if the user has access to the board.

    Access to the board is granted:
    - if access to the board is generally not restricted, or
    - if an access grant exists for the user and that board.
    """
    return db.session.scalar(
        select(
            select(DbBoard)
            .outerjoin(DbBoardAccessGrant)
            .filter(
                db.or_(
                    DbBoard.access_restricted == False,  # noqa: E712
                    DbBoardAccessGrant.user_id == user_id,
                )
            )
            .filter(DbBoard.id == board_id)
            .exists()
        )
    )
