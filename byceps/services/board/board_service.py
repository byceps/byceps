"""
byceps.services.board.board_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import BrandID

from ..brand import service as brand_service

from .dbmodels.board import Board as DbBoard
from .transfer.models import Board, BoardID


def create_board(brand_id: BrandID, board_id: BoardID) -> Board:
    """Create a board for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    board = DbBoard(board_id, brand.id)

    db.session.add(board)
    db.session.commit()

    return _db_entity_to_board(board)


def delete_board(board_id: BoardID) -> None:
    """Delete a board."""
    db.session.query(DbBoard) \
        .filter_by(id=board_id) \
        .delete()

    db.session.commit()


def find_board(board_id: BoardID) -> Optional[Board]:
    """Return the board with that id, or `None` if not found."""
    board = db.session.query(DbBoard).get(board_id)

    if board is None:
        return None

    return _db_entity_to_board(board)


def get_boards_for_brand(brand_id: BrandID) -> Sequence[Board]:
    """Return all boards that belong to the brand."""
    boards = DbBoard.query \
        .filter_by(brand_id=brand_id) \
        .all()

    return [_db_entity_to_board(board) for board in boards]


def _db_entity_to_board(board: DbBoard) -> Board:
    return Board(
        board.id,
        board.brand_id,
        board.access_restricted,
    )
