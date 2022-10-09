"""
byceps.services.board.board_category_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional, Sequence

from ...database import db

from .dbmodels.category import DbBoardCategory
from .transfer.models import (
    BoardCategory,
    BoardCategoryID,
    BoardCategoryWithLastUpdate,
    BoardID,
)


def count_categories_for_board(board_id: BoardID) -> int:
    """Return the number of categories for that board."""
    return db.session \
        .query(DbBoardCategory) \
        .filter_by(board_id=board_id) \
        .count()


def find_category_by_id(
    category_id: BoardCategoryID,
) -> Optional[BoardCategory]:
    """Return the category with that id, or `None` if not found."""
    category = db.session.get(DbBoardCategory, category_id)

    if category is None:
        return None

    return _db_entity_to_category(category)


def find_category_by_slug(
    board_id: BoardID, slug: str
) -> Optional[BoardCategory]:
    """Return the category for that board and slug, or `None` if not found."""
    category = db.session \
        .query(DbBoardCategory) \
        .filter_by(board_id=board_id) \
        .filter_by(slug=slug) \
        .first()

    if category is None:
        return None

    return _db_entity_to_category(category)


def get_categories(board_id: BoardID) -> Sequence[BoardCategory]:
    """Return all categories for that board, ordered by position."""
    categories = db.session \
        .query(DbBoardCategory) \
        .filter_by(board_id=board_id) \
        .order_by(DbBoardCategory.position) \
        .all()

    return [_db_entity_to_category(category) for category in categories]


def get_categories_excluding(
    board_id: BoardID, category_id: BoardCategoryID
) -> Sequence[BoardCategory]:
    """Return all categories for that board except for the specified one."""
    categories = db.session \
        .query(DbBoardCategory) \
        .filter_by(board_id=board_id) \
        .filter(DbBoardCategory.id != category_id) \
        .order_by(DbBoardCategory.position) \
        .all()

    return [_db_entity_to_category(category) for category in categories]


def get_categories_with_last_updates(
    board_id: BoardID,
) -> Sequence[BoardCategoryWithLastUpdate]:
    """Return the categories for that board.

    Include the creator of the last posting in each category.
    """
    categories_with_last_update = db.session \
        .query(DbBoardCategory) \
        .filter_by(board_id=board_id) \
        .filter_by(hidden=False) \
        .options(
            db.joinedload(DbBoardCategory.last_posting_updated_by),
        ) \
        .all()

    return [
        _db_entity_to_category_with_last_update(category)
        for category in categories_with_last_update
    ]


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


def _db_entity_to_category_with_last_update(
    category: DbBoardCategory,
) -> BoardCategoryWithLastUpdate:
    return BoardCategoryWithLastUpdate(
        category.id,
        category.board_id,
        category.position,
        category.slug,
        category.title,
        category.description,
        category.topic_count,
        category.posting_count,
        category.hidden,
        category.last_posting_updated_at,
        category.last_posting_updated_by,
    )
