"""
byceps.services.board.board_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import BrandID

from ..brand import service as brand_service

from .models.board import Board as DbBoard
from .transfer.models import BoardID


def create_board(brand_id: BrandID, board_id: BoardID) -> DbBoard:
    """Create a board for that brand."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        raise ValueError('Unknown brand ID "{}"'.format(brand_id))

    board = DbBoard(board_id, brand.id)

    db.session.add(board)
    db.session.commit()

    return board


def find_board(board_id: BoardID) -> Optional[DbBoard]:
    """Return the board with that id, or `None` if not found."""
    return DbBoard.query.get(board_id)


def get_boards_for_brand(brand_id: BrandID) -> Sequence[DbBoard]:
    """Return all boards that belong to the brand."""
    return DbBoard.query \
        .filter_by(brand_id=brand_id) \
        .all()
