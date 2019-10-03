"""
byceps.services.board.category_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db

from .models.category import Category as DbCategory
from .transfer.models import BoardID, Category, CategoryID, \
    CategoryWithLastUpdate


def count_categories_for_board(board_id: BoardID) -> int:
    """Return the number of categories for that board."""
    return DbCategory.query \
        .for_board(board_id) \
        .count()


def find_category_by_id(category_id: CategoryID) -> Optional[Category]:
    """Return the category with that id, or `None` if not found."""
    category = DbCategory.query.get(category_id)

    if category is None:
        return None

    return _db_entity_to_category(category)


def find_category_by_slug(board_id: BoardID, slug: str) -> Optional[Category]:
    """Return the category for that board and slug, or `None` if not found."""
    category = DbCategory.query \
        .for_board(board_id) \
        .filter_by(slug=slug) \
        .first()

    if category is None:
        return None

    return _db_entity_to_category(category)


def get_categories(board_id: BoardID) -> Sequence[Category]:
    """Return all categories for that board, ordered by position."""
    categories = DbCategory.query \
        .for_board(board_id) \
        .order_by(DbCategory.position) \
        .all()

    return [_db_entity_to_category(category) for category in categories]


def get_categories_excluding(
    board_id: BoardID, category_id: CategoryID
) -> Sequence[Category]:
    """Return all categories for that board except for the specified one."""
    categories = DbCategory.query \
        .for_board(board_id) \
        .filter(DbCategory.id != category_id) \
        .order_by(DbCategory.position) \
        .all()

    return [_db_entity_to_category(category) for category in categories]


def get_categories_with_last_updates(
    board_id: BoardID
) -> Sequence[CategoryWithLastUpdate]:
    """Return the categories for that board.

    Include the creator of the last posting in each category.
    """
    categories_with_last_update = DbCategory.query \
        .for_board(board_id) \
        .filter_by(hidden=False) \
        .options(
            db.joinedload(DbCategory.last_posting_updated_by),
        ) \
        .all()

    return [_db_entity_to_category_with_last_update(category)
            for category in categories_with_last_update]


def _db_entity_to_category(category: DbCategory) -> Category:
    return Category(
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
    category: DbCategory
) -> CategoryWithLastUpdate:
    return CategoryWithLastUpdate(
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
