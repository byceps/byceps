"""
byceps.services.board.board_topic_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.sql import Select

from ...database import db, paginate, Pagination

from .dbmodels.category import DbBoardCategory
from .dbmodels.posting import DbPosting
from .dbmodels.topic import DbTopic
from .models import BoardCategoryID, BoardID, TopicID


def count_topics_for_board(board_id: BoardID) -> int:
    """Return the number of topics for that board."""
    return db.session.scalar(
        select(db.func.count(DbTopic.id))
        .join(DbBoardCategory)
        .filter(DbBoardCategory.board_id == board_id)
    )


def find_topic_by_id(topic_id: TopicID) -> Optional[DbTopic]:
    """Return the topic with that id, or `None` if not found."""
    return db.session.get(DbTopic, topic_id)


def get_topic(topic_id: TopicID) -> DbTopic:
    """Return the topic with that id."""
    db_topic = find_topic_by_id(topic_id)

    if db_topic is None:
        raise ValueError(f'Unknown topic ID "{topic_id}"')

    return db_topic


def find_topic_visible_for_user(
    topic_id: TopicID, include_hidden: bool
) -> Optional[DbTopic]:
    """Return the topic with that id, or `None` if not found or
    invisible for the user.
    """
    stmt = (
        select(DbTopic)
        .options(
            db.joinedload(DbTopic.category),
        )
        .filter_by(id=topic_id)
    )

    if not include_hidden:
        stmt = stmt.filter_by(hidden=False)

    return db.session.scalars(stmt).unique().first()


def get_recent_topics(
    board_id: BoardID, include_hidden: bool, limit: int
) -> list[DbTopic]:
    """Return recent topics in that board."""
    return (
        db.session.scalars(
            _select_topics(include_hidden)
            .join(DbBoardCategory)
            .filter(DbBoardCategory.board_id == board_id)
            .filter(DbBoardCategory.hidden == False)  # noqa: E712
            .order_by(DbTopic.last_updated_at.desc())
            .limit(limit)
        )
        .unique()
        .all()
    )


def paginate_topics(
    board_id: BoardID, include_hidden: bool, page: int, per_page: int
) -> Pagination:
    """Paginate topics in that board."""
    items_stmt = (
        _select_topics(include_hidden)
        .join(DbBoardCategory)
        .filter(DbBoardCategory.board_id == board_id)
        .filter(DbBoardCategory.hidden == False)  # noqa: E712
        .order_by(DbTopic.last_updated_at.desc())
    )

    count_stmt = (
        _count_topics(include_hidden)
        .join(DbBoardCategory)
        .filter(DbBoardCategory.board_id == board_id)
        .filter(DbBoardCategory.hidden == False)  # noqa: E712
    )

    return paginate(
        items_stmt,
        count_stmt,
        page,
        per_page,
        scalar_result=True,
        unique_result=True,
    )


def get_all_topic_ids_in_category(category_id: BoardCategoryID) -> set[TopicID]:
    """Return the IDs of all topics in the category."""
    topic_ids = db.session.scalars(
        select(DbTopic.id).filter(DbTopic.category_id == category_id)
    ).all()

    return set(topic_ids)


def paginate_topics_of_category(
    category_id: BoardCategoryID,
    include_hidden: bool,
    page: int,
    per_page: int,
) -> Pagination:
    """Paginate topics in that category, as visible for the user.

    Pinned topics are returned first.
    """
    items_stmt = (
        _select_topics(include_hidden)
        .filter_by(category_id=category_id)
        .order_by(DbTopic.pinned.desc(), DbTopic.last_updated_at.desc())
    )

    count_stmt = _count_topics(include_hidden).filter_by(
        category_id=category_id
    )

    return paginate(
        items_stmt,
        count_stmt,
        page,
        per_page,
        scalar_result=True,
        unique_result=True,
    )


def _select_topics(include_hidden: bool) -> Select:
    stmt = select(DbTopic).options(
        db.joinedload(DbTopic.category),
        db.joinedload(DbTopic.last_updated_by),
        db.joinedload(DbTopic.hidden_by),
        db.joinedload(DbTopic.locked_by),
        db.joinedload(DbTopic.pinned_by),
    )

    if not include_hidden:
        stmt = stmt.filter_by(hidden=False)

    return stmt


def _count_topics(include_hidden: bool) -> Select:
    stmt = select(db.func.count(DbTopic.id))

    if not include_hidden:
        stmt = stmt.filter_by(hidden=False)

    return stmt


def find_default_posting_to_jump_to(
    topic_id: TopicID, include_hidden: bool, last_viewed_at: datetime
) -> Optional[DbPosting]:
    """Return the posting of the topic to show by default, or `None`."""
    postings_stmt = select(DbPosting).filter_by(topic_id=topic_id)

    if not include_hidden:
        postings_stmt = postings_stmt.filter_by(hidden=False)

    first_new_posting = db.session.scalars(
        postings_stmt.filter(DbPosting.created_at > last_viewed_at).order_by(
            DbPosting.created_at.asc()
        )
    ).first()

    if first_new_posting is None:
        # Current user has seen all postings so far, so show the last one.
        return db.session.scalars(
            postings_stmt.order_by(DbPosting.created_at.desc())
        ).first()

    return first_new_posting
