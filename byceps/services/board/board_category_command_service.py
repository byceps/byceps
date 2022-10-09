"""
byceps.services.board.board_category_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db

from . import board_topic_query_service
from .dbmodels.board import DbBoard
from .dbmodels.category import DbBoardCategory
from .transfer.models import BoardCategory, BoardCategoryID, BoardID


def create_category(
    board_id: BoardID, slug: str, title: str, description: str
) -> BoardCategory:
    """Create a category in that board."""
    board = db.session.get(DbBoard, board_id)
    if board is None:
        raise ValueError(f'Unknown board ID "{board_id}"')

    category = DbBoardCategory(board.id, slug, title, description)
    board.categories.append(category)

    db.session.commit()

    return _db_entity_to_category(category)


def update_category(
    category_id: BoardCategoryID, slug: str, title: str, description: str
) -> BoardCategory:
    """Update the category."""
    category = _get_category(category_id)

    category.slug = slug.strip().lower()
    category.title = title.strip()
    category.description = description.strip()

    db.session.commit()

    return _db_entity_to_category(category)


def hide_category(category_id: BoardCategoryID) -> None:
    """Hide the category."""
    category = _get_category(category_id)

    category.hidden = True
    db.session.commit()


def unhide_category(category_id: BoardCategoryID) -> None:
    """Un-hide the category."""
    category = _get_category(category_id)

    category.hidden = False
    db.session.commit()


def move_category_up(category_id: BoardCategoryID) -> None:
    """Move a category upwards by one position."""
    category = _get_category(category_id)

    category_list = category.board.categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()


def move_category_down(category_id: BoardCategoryID) -> None:
    """Move a category downwards by one position."""
    category = _get_category(category_id)

    category_list = category.board.categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()


def delete_category(category_id: BoardCategoryID) -> None:
    """Delete category."""
    category = _get_category(category_id)

    topic_ids = board_topic_query_service.get_all_topic_ids_in_category(
        category.id
    )
    if topic_ids:
        raise ValueError(
            f'Category "{category.title}" in board "{category.board_id}" '
            'contains topics. It will not be deleted because of that.'
        )

    db.session.delete(category)
    db.session.commit()


def _get_category(category_id: BoardCategoryID) -> DbBoardCategory:
    category = db.session.get(DbBoardCategory, category_id)

    if category is None:
        raise ValueError(f'Unknown category ID "{category_id}"')

    return category


def _db_entity_to_category(category: DbBoardCategory) -> BoardCategory:
    return BoardCategory(
        category.id,
        category.board_id,
        category.position,
        category.slug,
        category.title,
        category.description,
        category.topic_count,
        category.posting_count,
        category.hidden,
    )
