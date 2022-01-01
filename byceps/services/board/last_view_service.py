"""
byceps.services.board.last_view_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from ...database import db, upsert, upsert_many
from ...typing import UserID

from .dbmodels.last_category_view import LastCategoryView
from .dbmodels.last_topic_view import LastTopicView
from .dbmodels.topic import Topic as DbTopic
from . import topic_query_service
from .transfer.models import CategoryID, CategoryWithLastUpdate, TopicID


# -------------------------------------------------------------------- #
# categories


def contains_category_unseen_postings(
    category: CategoryWithLastUpdate, user_id: UserID
) -> bool:
    """Return `True` if the category contains postings created after the
    last time the user viewed it.
    """
    if category.last_posting_updated_at is None:
        return False

    last_view = find_last_category_view(user_id, category.id)

    if last_view is None:
        return True

    return category.last_posting_updated_at > last_view.occurred_at


def find_last_category_view(
    user_id: UserID, category_id: CategoryID
) -> Optional[LastCategoryView]:
    """Return the user's last view of the category, or `None` if not found."""
    return db.session \
        .query(LastCategoryView) \
        .filter_by(user_id=user_id, category_id=category_id) \
        .first()


def mark_category_as_just_viewed(
    category_id: CategoryID, user_id: UserID
) -> None:
    """Mark the category as last viewed by the user (if logged in) at
    the current time.
    """
    table = LastCategoryView.__table__
    identifier = {
        'user_id': user_id,
        'category_id': category_id,
    }
    replacement = {
        'occurred_at': datetime.utcnow(),
    }

    upsert(table, identifier, replacement)


def delete_last_category_views(category_id: CategoryID) -> None:
    """Delete the category's last views."""
    db.session.query(LastCategoryView) \
        .filter_by(category_id=category_id) \
        .delete()
    db.session.commit()


# -------------------------------------------------------------------- #
# topics


def contains_topic_unseen_postings(topic: DbTopic, user_id: UserID) -> bool:
    """Return `True` if the topic contains postings created after the
    last time the user viewed it.
    """
    last_viewed_at = find_topic_last_viewed_at(topic.id, user_id)

    return last_viewed_at is None or topic.last_updated_at > last_viewed_at


def find_last_topic_view(
    user_id: UserID, topic_id: TopicID
) -> Optional[LastTopicView]:
    """Return the user's last view of the topic, or `None` if not found."""
    return db.session \
        .query(LastTopicView) \
        .filter_by(user_id=user_id, topic_id=topic_id) \
        .first()


def find_topic_last_viewed_at(
    topic_id: TopicID, user_id: UserID
) -> Optional[datetime]:
    """Return the time the topic was last viewed by the user (or
    nothing, if it hasn't been viewed by the user yet).
    """
    last_view = find_last_topic_view(user_id, topic_id)
    return last_view.occurred_at if (last_view is not None) else None


def mark_topic_as_just_viewed(topic_id: TopicID, user_id: UserID) -> None:
    """Mark the topic as last viewed by the user (if logged in) at the
    current time.
    """
    table = LastTopicView.__table__
    identifier = {
        'user_id': user_id,
        'topic_id': topic_id,
    }
    replacement = {
        'occurred_at': datetime.utcnow(),
    }

    upsert(table, identifier, replacement)


def mark_all_topics_in_category_as_viewed(
    category_id: CategoryID, user_id: UserID
) -> None:
    """Mark all topics in the category as viewed."""
    topic_ids = topic_query_service.get_all_topic_ids_in_category(category_id)

    if not topic_ids:
        return

    table = LastTopicView.__table__
    replacement = {
        'occurred_at': datetime.utcnow(),
    }

    identifiers = [
        {'user_id': user_id, 'topic_id': topic_id} for topic_id in topic_ids
    ]

    upsert_many(table, identifiers, replacement)


def delete_last_topic_views(topic_id: TopicID) -> None:
    """Delete the topic's last views."""
    db.session.query(LastTopicView) \
        .filter_by(topic_id=topic_id) \
        .delete()
    db.session.commit()
