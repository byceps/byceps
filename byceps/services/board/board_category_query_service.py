"""
byceps.services.board.board_category_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import select

from byceps.database import db

from .dbmodels.category import DbBoardCategory
from .models import (
    BoardCategory,
    BoardCategoryID,
    BoardCategoryWithLastUpdate,
    BoardID,
)


def count_categories_for_board(board_id: BoardID) -> int:
    """Return the number of categories for that board."""
    return db.session.scalar(
        select(db.func.count(DbBoardCategory.id)).filter_by(board_id=board_id)
    )


def find_category_by_id(
    category_id: BoardCategoryID,
) -> Optional[BoardCategory]:
    """Return the category with that id, or `None` if not found."""
    db_category = db.session.get(DbBoardCategory, category_id)

    if db_category is None:
        return None

    return _db_entity_to_category(db_category)


def find_category_by_slug(
    board_id: BoardID, slug: str
) -> Optional[BoardCategory]:
    """Return the category for that board and slug, or `None` if not found."""
    db_category = db.session.scalars(
        select(DbBoardCategory)
        .filter_by(board_id=board_id)
        .filter_by(slug=slug)
    ).first()

    if db_category is None:
        return None

    return _db_entity_to_category(db_category)


def get_categories(board_id: BoardID) -> list[BoardCategory]:
    """Return all categories for that board, ordered by position."""
    db_categories = db.session.scalars(
        select(DbBoardCategory)
        .filter_by(board_id=board_id)
        .order_by(DbBoardCategory.position)
    ).all()

    return [
        _db_entity_to_category(db_category) for db_category in db_categories
    ]


def get_categories_excluding(
    board_id: BoardID, category_id: BoardCategoryID
) -> list[BoardCategory]:
    """Return all categories for that board except for the specified one."""
    db_categories = db.session.scalars(
        select(DbBoardCategory)
        .filter_by(board_id=board_id)
        .filter(DbBoardCategory.id != category_id)
        .order_by(DbBoardCategory.position)
    ).all()

    return [
        _db_entity_to_category(db_category) for db_category in db_categories
    ]


def get_categories_with_last_updates(
    board_id: BoardID,
) -> list[BoardCategoryWithLastUpdate]:
    """Return the categories for that board.

    Include the creator of the last posting in each category.
    """
    db_categories_with_last_update = (
        db.session.scalars(
            select(DbBoardCategory)
            .filter_by(board_id=board_id)
            .filter_by(hidden=False)
            .options(
                db.joinedload(DbBoardCategory.last_posting_updated_by),
            )
        )
        .unique()
        .all()
    )

    return [
        _db_entity_to_category_with_last_update(db_category)
        for db_category in db_categories_with_last_update
    ]


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


def _db_entity_to_category_with_last_update(
    db_category: DbBoardCategory,
) -> BoardCategoryWithLastUpdate:
    return BoardCategoryWithLastUpdate(
        id=db_category.id,
        board_id=db_category.board_id,
        position=db_category.position,
        slug=db_category.slug,
        title=db_category.title,
        description=db_category.description,
        topic_count=db_category.topic_count,
        posting_count=db_category.posting_count,
        hidden=db_category.hidden,
        last_posting_updated_at=db_category.last_posting_updated_at,
        last_posting_updated_by=db_category.last_posting_updated_by,
    )
