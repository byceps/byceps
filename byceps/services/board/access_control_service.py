"""
byceps.services.board.access_control_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...typing import UserID

from .models.board import Board
from .models.board_access_grant import BoardAccessGrant, BoardAccessGrantID
from .transfer.models import BoardID


def grant_access_to_board(
    board_id: BoardID, user_id: UserID
) -> BoardAccessGrantID:
    """Grant the user access to the board."""
    grant = BoardAccessGrant(board_id, user_id)

    db.session.add(grant)
    db.session.commit()

    return grant.id


def revoke_access_to_board(grant_id: BoardAccessGrantID) -> None:
    """Revoke the user's access to the board."""
    grant = BoardAccessGrant.query.get(grant_id)

    if grant is None:
        raise ValueError(f"Unknown board grant ID '{grant_id}'")

    db.session.delete(grant)
    db.session.commit()


def has_user_access_to_board(user_id: UserID, board_id: BoardID) -> bool:
    """Return `True` if the user has access to the board.

    Access to the board is granted:
    - if access to the board is generally not restricted, or
    - if an access grant exists for the user and that board.
    """
    subquery = Board.query \
        .outerjoin(BoardAccessGrant) \
        .filter(
            db.or_(
                Board.access_restricted == False,
                BoardAccessGrant.user_id == user_id,
            )
        ) \
        .filter(Board.id == board_id) \
        .exists()

    return db.session.query(subquery).scalar()
