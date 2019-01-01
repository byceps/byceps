"""
byceps.services.board.category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db

from .models.board import Board as DbBoard
from .models.category import Category as DbCategory
from .transfer.models import BoardID, Category, CategoryID, \
    CategoryWithLastUpdate


def create_category(board_id: BoardID, slug: str, title: str, description: str
                   ) -> Category:
    """Create a category in that board."""
    board = DbBoard.query.get(board_id)
    if board is None:
        raise ValueError('Unknown board ID "{}"'.format(board_id))

    category = DbCategory(board.id, slug, title, description)
    board.categories.append(category)

    db.session.commit()

    return _db_entity_to_category(category)


def update_category(category_id: CategoryID, slug: str, title: str,
                    description: str
                   ) -> Category:
    """Update the category."""
    category = _get_category(category_id)

    category.slug = slug.strip().lower()
    category.title = title.strip()
    category.description = description.strip()

    db.session.commit()

    return _db_entity_to_category(category)


def move_category_up(category_id: CategoryID) -> None:
    """Move a category upwards by one position."""
    category = _get_category(category_id)

    category_list = category.board.categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()


def move_category_down(category_id: CategoryID) -> None:
    """Move a category downwards by one position."""
    category = _get_category(category_id)

    category_list = category.board.categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()


def _get_category(category_id: CategoryID) -> DbCategory:
    category = DbCategory.query.get(category_id)

    if category is None:
        raise ValueError('Unknown category ID "{}"'.format(category_id))

    return category


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


def get_categories_excluding(board_id: BoardID, category_id: CategoryID
                            ) -> Sequence[Category]:
    """Return all categories for that board except for the specified one."""
    categories = DbCategory.query \
        .for_board(board_id) \
        .filter(DbCategory.id != category_id) \
        .order_by(DbCategory.position) \
        .all()

    return [_db_entity_to_category(category) for category in categories]


def get_categories_with_last_updates(board_id: BoardID
                                    ) -> Sequence[CategoryWithLastUpdate]:
    """Return the categories for that board.

    Include the creator of the last posting in each category.
    """
    categories_with_last_update = DbCategory.query \
        .for_board(board_id) \
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
    )


def _db_entity_to_category_with_last_update(category: DbCategory
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
        category.last_posting_updated_at,
        category.last_posting_updated_by,
    )
