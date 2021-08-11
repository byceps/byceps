"""
byceps.services.board.topic_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from ...database import db, Pagination, Query

from .dbmodels.category import Category as DbCategory
from .dbmodels.posting import Posting as DbPosting
from .dbmodels.topic import Topic as DbTopic
from .transfer.models import BoardID, CategoryID, TopicID


def count_topics_for_board(board_id: BoardID) -> int:
    """Return the number of topics for that board."""
    return DbTopic.query \
        .join(DbCategory) \
            .filter(DbCategory.board_id == board_id) \
        .count()


def find_topic_by_id(topic_id: TopicID) -> Optional[DbTopic]:
    """Return the topic with that id, or `None` if not found."""
    return db.session.query(DbTopic).get(topic_id)


def get_topic(topic_id: TopicID) -> DbTopic:
    """Return the topic with that id."""
    topic = find_topic_by_id(topic_id)

    if topic is None:
        raise ValueError(f'Unknown topic ID "{topic_id}"')

    return topic


def find_topic_visible_for_user(
    topic_id: TopicID, include_hidden: bool
) -> Optional[DbTopic]:
    """Return the topic with that id, or `None` if not found or
    invisible for the user.
    """
    query = DbTopic.query \
        .options(
            db.joinedload(DbTopic.category),
        )

    if not include_hidden:
        query = query.filter_by(hidden=False)

    return query \
        .filter_by(id=topic_id) \
        .first()


def get_recent_topics(
    board_id: BoardID, include_hidden: bool, limit: int
) -> list[DbTopic]:
    """Paginate topics in that board."""
    return _query_topics(include_hidden) \
        .join(DbCategory) \
            .filter(DbCategory.board_id == board_id) \
            .filter(DbCategory.hidden == False) \
        .order_by(DbTopic.last_updated_at.desc()) \
        .limit(limit) \
        .all()


def paginate_topics(
    board_id: BoardID, include_hidden: bool, page: int, topics_per_page: int
) -> Pagination:
    """Paginate topics in that board."""
    return _query_topics(include_hidden) \
        .join(DbCategory) \
            .filter(DbCategory.board_id == board_id) \
            .filter(DbCategory.hidden == False) \
        .order_by(DbTopic.last_updated_at.desc()) \
        .paginate(page, topics_per_page)


def get_all_topic_ids_in_category(category_id: CategoryID) -> set[TopicID]:
    """Return the IDs of all topics in the category."""
    rows = db.session \
        .query(DbTopic.id) \
        .filter(DbTopic.category_id == category_id) \
        .all()

    return {row[0] for row in rows}


def paginate_topics_of_category(
    category_id: CategoryID,
    include_hidden: bool,
    page: int,
    topics_per_page: int,
) -> Pagination:
    """Paginate topics in that category, as visible for the user.

    Pinned topics are returned first.
    """
    return _query_topics(include_hidden) \
        .filter_by(category_id=category_id) \
        .order_by(DbTopic.pinned.desc(), DbTopic.last_updated_at.desc()) \
        .paginate(page, topics_per_page)


def _query_topics(include_hidden: bool) -> Query:
    query = DbTopic.query \
        .options(
            db.joinedload(DbTopic.category),
            db.joinedload(DbTopic.last_updated_by),
            db.joinedload(DbTopic.hidden_by),
            db.joinedload(DbTopic.locked_by),
            db.joinedload(DbTopic.pinned_by),
        )

    if not include_hidden:
        query = query.filter_by(hidden=False)

    return query


def find_default_posting_to_jump_to(
    topic_id: TopicID, include_hidden: bool, last_viewed_at: datetime
) -> Optional[DbPosting]:
    """Return the posting of the topic to show by default, or `None`."""
    postings_query = DbPosting.query \
        .filter_by(topic_id=topic_id)

    if not include_hidden:
        postings_query = postings_query.filter_by(hidden=False)

    first_new_posting = postings_query \
        .filter(DbPosting.created_at > last_viewed_at) \
        .order_by(DbPosting.created_at.asc()) \
        .first()

    if first_new_posting is None:
        # Current user has seen all postings so far, so show the last one.
        return postings_query \
            .order_by(DbPosting.created_at.desc()) \
            .first()

    return first_new_posting
