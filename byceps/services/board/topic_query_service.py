"""
byceps.services.board.topic_query_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional, Set

from ...database import db, Pagination, Query

from ..authentication.session.models.current_user import CurrentUser

from .models.category import Category as DbCategory
from .models.posting import Posting as DbPosting
from .models.topic import Topic as DbTopic
from .transfer.models import BoardID, CategoryID, TopicID


def count_topics_for_board(board_id: BoardID) -> int:
    """Return the number of topics for that board."""
    return DbTopic.query \
        .join(DbCategory) \
            .filter(DbCategory.board_id == board_id) \
        .count()


def find_topic_by_id(topic_id: TopicID) -> Optional[DbTopic]:
    """Return the topic with that id, or `None` if not found."""
    return DbTopic.query.get(topic_id)


def get_topic(topic_id: TopicID) -> DbTopic:
    """Return the topic with that id."""
    topic = find_topic_by_id(topic_id)

    if topic is None:
        raise ValueError(f'Unknown topic ID "{topic_id}"')

    return topic


def find_topic_visible_for_user(
    topic_id: TopicID, user: CurrentUser
) -> Optional[DbTopic]:
    """Return the topic with that id, or `None` if not found or
    invisible for the user.
    """
    return DbTopic.query \
        .options(
            db.joinedload(DbTopic.category),
        ) \
        .only_visible_for_user(user) \
        .filter_by(id=topic_id) \
        .first()


def paginate_topics(
    board_id: BoardID, user: CurrentUser, page: int, topics_per_page: int
) -> Pagination:
    """Paginate topics in that board, as visible for the user."""
    return _query_topics(user) \
        .join(DbCategory) \
            .filter(DbCategory.board_id == board_id) \
            .filter(DbCategory.hidden == False) \
        .order_by(DbTopic.last_updated_at.desc()) \
        .paginate(page, topics_per_page)


def get_all_topic_ids_in_category(category_id: CategoryID) -> Set[TopicID]:
    """Return the IDs of all topics in the category."""
    rows = db.session \
        .query(DbTopic.id) \
        .filter(DbTopic.category_id == category_id) \
        .all()

    return {row[0] for row in rows}


def paginate_topics_of_category(
    category_id: CategoryID, user: CurrentUser, page: int, topics_per_page: int
) -> Pagination:
    """Paginate topics in that category, as visible for the user.

    Pinned topics are returned first.
    """
    return _query_topics(user) \
        .for_category(category_id) \
        .order_by(DbTopic.pinned.desc(), DbTopic.last_updated_at.desc()) \
        .paginate(page, topics_per_page)


def _query_topics(user: CurrentUser) -> Query:
    return DbTopic.query \
        .options(
            db.joinedload(DbTopic.category),
            db.joinedload(DbTopic.last_updated_by),
            db.joinedload(DbTopic.hidden_by),
            db.joinedload(DbTopic.locked_by),
            db.joinedload(DbTopic.pinned_by),
        ) \
        .only_visible_for_user(user)


def find_default_posting_to_jump_to(
    topic_id: TopicID, user: CurrentUser, last_viewed_at: Optional[datetime]
) -> Optional[DbPosting]:
    """Return the posting of the topic to show by default, or `None`."""
    if user.is_anonymous:
        # All postings are potentially new to a guest, so start on
        # the first page.
        return None

    if last_viewed_at is None:
        # This topic is completely new to the current user, so
        # start on the first page.
        return None

    postings_query = DbPosting.query \
        .for_topic(topic_id) \
        .only_visible_for_user(user)

    first_new_posting = postings_query \
        .filter(DbPosting.created_at > last_viewed_at) \
        .earliest_to_latest() \
        .first()

    if first_new_posting is None:
        # Current user has seen all postings so far, so show the last one.
        return postings_query \
            .latest_to_earliest() \
            .first()

    return first_new_posting
