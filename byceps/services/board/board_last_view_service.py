"""
byceps.services.board.board_last_view_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db, upsert, upsert_many
from byceps.services.user.models.user import UserID

from . import board_topic_query_service
from .dbmodels.category import DbLastCategoryView
from .dbmodels.topic import DbTopic, DbLastTopicView
from .models import BoardCategoryID, BoardCategorySummary, TopicID


# -------------------------------------------------------------------- #
# categories


def contains_category_unseen_postings(
    category: BoardCategorySummary, user_id: UserID
) -> bool:
    """Return `True` if the category contains postings created after the
    last time the user viewed it.
    """
    if category.last_posting_updated_at is None:
        return False

    db_last_view = find_last_category_view(user_id, category.id)

    if db_last_view is None:
        return True

    return category.last_posting_updated_at > db_last_view.occurred_at


def find_last_category_view(
    user_id: UserID, category_id: BoardCategoryID
) -> DbLastCategoryView | None:
    """Return the user's last view of the category, or `None` if not found."""
    return db.session.scalars(
        select(DbLastCategoryView).filter_by(
            user_id=user_id, category_id=category_id
        )
    ).first()


# -------------------------------------------------------------------- #
# topics


def contains_topic_unseen_postings(db_topic: DbTopic, user_id: UserID) -> bool:
    """Return `True` if the topic contains postings created after the
    last time the user viewed it.
    """
    last_viewed_at = find_topic_last_viewed_at(db_topic.id, user_id)
    return last_viewed_at is None or db_topic.last_updated_at > last_viewed_at


def find_topic_last_viewed_at(
    topic_id: TopicID, user_id: UserID
) -> datetime | None:
    """Return the time the topic was last viewed by the user (or
    nothing, if it hasn't been viewed by the user yet).
    """
    db_last_view = db.session.scalars(
        select(DbLastTopicView).filter_by(user_id=user_id, topic_id=topic_id)
    ).first()

    return db_last_view.occurred_at if (db_last_view is not None) else None


def mark_topic_as_just_viewed(topic_id: TopicID, user_id: UserID) -> None:
    """Mark the topic as last viewed by the user (if logged in) at the
    current time.
    """
    table = DbLastTopicView.__table__
    identifier = {
        'user_id': user_id,
        'topic_id': topic_id,
    }
    replacement = {
        'occurred_at': datetime.utcnow(),
    }

    upsert(table, identifier, replacement)


def mark_all_topics_as_viewed(user_id: UserID) -> None:
    """Mark all topics as viewed by the current user."""
    topic_ids = board_topic_query_service.get_all_topic_ids()

    _mark_topics_as_viewed(topic_ids, user_id)


def mark_all_topics_in_category_as_viewed(
    category_id: BoardCategoryID, user_id: UserID
) -> None:
    """Mark all topics in the category as viewed by the current user."""
    topic_ids = board_topic_query_service.get_all_topic_ids_in_category(
        category_id
    )

    _mark_topics_as_viewed(topic_ids, user_id)


def _mark_topics_as_viewed(topic_ids: set[TopicID], user_id: UserID) -> None:
    if not topic_ids:
        return

    table = DbLastTopicView.__table__
    replacement = {
        'occurred_at': datetime.utcnow(),
    }

    identifiers = [
        {'user_id': user_id, 'topic_id': topic_id} for topic_id in topic_ids
    ]

    upsert_many(table, identifiers, replacement)


def delete_last_topic_views(topic_id: TopicID) -> None:
    """Delete the topic's last views."""
    db.session.execute(delete(DbLastTopicView).filter_by(topic_id=topic_id))
    db.session.commit()
