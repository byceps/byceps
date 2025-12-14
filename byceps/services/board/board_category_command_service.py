"""
byceps.services.board.board_category_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid4

from . import board_topic_query_service
from .dbmodels.board import DbBoard
from .dbmodels.category import DbBoardCategory
from .errors import (
    BoardCategoryAlreadyAtBottomError,
    BoardCategoryAlreadyAtTopError,
)
from .models import BoardCategory, BoardCategoryID, BoardID


def create_category(
    board_id: BoardID, slug: str, title: str, description: str
) -> BoardCategory:
    """Create a category in that board."""
    db_board = db.session.get(DbBoard, board_id)
    if db_board is None:
        raise ValueError(f'Unknown board ID "{board_id}"')

    category_id = BoardCategoryID(generate_uuid4())

    db_category = DbBoardCategory(
        category_id, db_board.id, slug, title, description
    )
    db_board.categories.append(db_category)

    db.session.commit()

    return _db_entity_to_category(db_category)


def update_category(
    category_id: BoardCategoryID, slug: str, title: str, description: str
) -> BoardCategory:
    """Update the category."""
    db_category = _get_db_category(category_id)

    db_category.slug = slug
    db_category.title = title
    db_category.description = description

    db.session.commit()

    return _db_entity_to_category(db_category)


def hide_category(category_id: BoardCategoryID) -> None:
    """Hide the category."""
    db_category = _get_db_category(category_id)

    db_category.hidden = True
    db.session.commit()


def unhide_category(category_id: BoardCategoryID) -> None:
    """Un-hide the category."""
    db_category = _get_db_category(category_id)

    db_category.hidden = False
    db.session.commit()


def move_category_up(
    category_id: BoardCategoryID,
) -> Result[None, BoardCategoryAlreadyAtTopError]:
    """Move a category upwards by one position."""
    db_category = _get_db_category(category_id)

    category_list = db_category.board.categories

    if db_category.position == 1:
        return Err(BoardCategoryAlreadyAtTopError())

    db_popped_category = category_list.pop(db_category.position - 1)
    category_list.insert(db_popped_category.position - 2, db_popped_category)

    db.session.commit()

    return Ok(None)


def move_category_down(
    category_id: BoardCategoryID,
) -> Result[None, BoardCategoryAlreadyAtBottomError]:
    """Move a category downwards by one position."""
    db_category = _get_db_category(category_id)

    category_list = db_category.board.categories

    if db_category.position == len(category_list):
        return Err(BoardCategoryAlreadyAtBottomError())

    db_popped_category = category_list.pop(db_category.position - 1)
    category_list.insert(db_popped_category.position, db_popped_category)

    db.session.commit()

    return Ok(None)


def delete_category(category_id: BoardCategoryID) -> Result[None, str]:
    """Delete category."""
    db_category = _get_db_category(category_id)

    topic_ids = board_topic_query_service.get_all_topic_ids_in_category(
        db_category.id
    )
    if topic_ids:
        return Err(
            f'Category "{db_category.title}" in board "{db_category.board_id}" '
            'contains topics. It will not be deleted because of that.'
        )

    db.session.delete(db_category)
    db.session.commit()

    return Ok(None)


def _get_db_category(category_id: BoardCategoryID) -> DbBoardCategory:
    db_category = db.session.get(DbBoardCategory, category_id)

    if db_category is None:
        raise ValueError(f'Unknown category ID "{category_id}"')

    return db_category


def _db_entity_to_category(db_category: DbBoardCategory) -> BoardCategory:
    return BoardCategory(
        id=db_category.id,
        board_id=db_category.board_id,
        position=db_category.position,
        slug=db_category.slug,
        title=db_category.title,
        description=db_category.description,
        topic_count=db_category.topic_count,
        posting_count=db_category.posting_count,
        hidden=db_category.hidden,
    )
