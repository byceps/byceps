"""
byceps.services.board.board_category_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.services.authn.session.models import CurrentUser
from byceps.services.user.models import UserID

from .dbmodels.category import DbBoardCategory, DbLastCategoryView
from .models import (
    BoardCategory,
    BoardCategoryID,
    BoardCategorySummary,
    BoardID,
)


def count_categories_for_board(board_id: BoardID) -> int:
    """Return the number of categories for that board."""
    return (
        db.session.scalar(
            select(db.func.count(DbBoardCategory.id)).filter_by(
                board_id=board_id
            )
        )
        or 0
    )


def find_category_by_id(
    category_id: BoardCategoryID,
) -> BoardCategory | None:
    """Return the category with that ID, or `None` if not found."""
    db_category = db.session.get(DbBoardCategory, category_id)

    if db_category is None:
        return None

    return _db_entity_to_category(db_category)


def find_category_by_slug(board_id: BoardID, slug: str) -> BoardCategory | None:
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


def get_category_summaries(
    board_id: BoardID, current_user: CurrentUser
) -> list[BoardCategorySummary]:
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

    summaries = []

    for db_category in db_categories_with_last_update:
        contains_unseen_postings = contains_category_unseen_postings(
            db_category.id, db_category.last_posting_updated_at, current_user
        )

        summary = _db_entity_to_category_summary(
            db_category, contains_unseen_postings
        )

        summaries.append(summary)

    return summaries


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


def _db_entity_to_category_summary(
    db_category: DbBoardCategory, contains_unseen_postings: bool
) -> BoardCategorySummary:
    return BoardCategorySummary(
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
        contains_unseen_postings=contains_unseen_postings,
    )


# last view


def contains_category_unseen_postings(
    category_id: BoardCategoryID,
    last_posting_updated_at: datetime | None,
    current_user: CurrentUser,
) -> bool:
    """Return `True` if the category contains postings created after the
    last time the current user viewed it.
    """
    if last_posting_updated_at is None:
        return False

    if not current_user.authenticated:
        return False

    db_last_view = _find_last_category_view(current_user.id, category_id)

    if db_last_view is None:
        return True

    return last_posting_updated_at > db_last_view.occurred_at


def _find_last_category_view(
    user_id: UserID, category_id: BoardCategoryID
) -> DbLastCategoryView | None:
    """Return the user's last view of the category, or `None` if not found."""
    return db.session.scalars(
        select(DbLastCategoryView).filter_by(
            user_id=user_id, category_id=category_id
        )
    ).first()
