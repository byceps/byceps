"""
byceps.services.board.category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db

from . import board_service
from .models.board import BoardID
from .models.category import Category, CategoryID


def create_category(board_id: BoardID, slug: str, title: str, description: str
                   ) -> Category:
    """Create a category in that board."""
    board = board_service.find_board(board_id)
    if board is None:
        raise ValueError('Unknown board ID "{}"'.format(board_id))

    category = Category(board.id, slug, title, description)
    board.categories.append(category)

    db.session.commit()

    return category


def update_category(category: Category, slug: str, title: str, description: str
                   ) -> Category:
    """Update the category."""
    category.slug = slug.strip().lower()
    category.title = title.strip()
    category.description = description.strip()

    db.session.commit()

    return category


def move_category_up(category: Category) -> None:
    """Move a category upwards by one position."""
    category_list = category.board.categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()


def move_category_down(category: Category) -> None:
    """Move a category downwards by one position."""
    category_list = category.board.categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()


def count_categories_for_board(board_id: BoardID) -> int:
    """Return the number of categories for that board."""
    return Category.query.for_board_id(board_id).count()


def find_category_by_id(category_id: CategoryID) -> Optional[Category]:
    """Return the category with that id, or `None` if not found."""
    return Category.query.get(category_id)


def find_category_by_slug(board_id: BoardID, slug: str) -> Optional[Category]:
    """Return the category for that board and slug, or `None` if not found."""
    return Category.query \
        .for_board_id(board_id) \
        .filter_by(slug=slug) \
        .first()


def get_categories(board_id: BoardID) -> Sequence[Category]:
    """Return all categories for that board, ordered by position."""
    return Category.query \
        .for_board_id(board_id) \
        .order_by(Category.position) \
        .all()


def get_categories_excluding(board_id: BoardID, category_id: CategoryID
                            ) -> Sequence[Category]:
    """Return all categories for that board except for the specified one."""
    return Category.query \
        .for_board_id(board_id) \
        .filter(Category.id != category_id) \
        .order_by(Category.position) \
        .all()


def get_categories_with_last_updates(board_id: BoardID) -> Sequence[Category]:
    """Return the categories for that board.

    Include the creator of the last posting in each category.
    """
    return Category.query \
        .for_board_id(board_id) \
        .options(
            db.joinedload(Category.last_posting_updated_by),
        ) \
        .all()
