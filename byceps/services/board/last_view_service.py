"""
byceps.services.board.last_view_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from ...database import db
from ...typing import UserID

from .models.category import Category, CategoryID
from .models.last_category_view import LastCategoryView
from .models.last_topic_view import LastTopicView
from .models.topic import Topic, TopicID
from . import topic_service


# -------------------------------------------------------------------- #
# categories


def contains_category_unseen_postings(category: Category, user_id: UserID
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


def find_last_category_view(user_id: UserID, category_id: CategoryID
                           ) -> Optional[LastCategoryView]:
    """Return the user's last view of the category, or `None` if not found."""
    return LastCategoryView.query \
        .filter_by(user_id=user_id, category_id=category_id) \
        .first()


def mark_category_as_just_viewed(category_id: CategoryID, user_id: UserID
                                ) -> None:
    """Mark the category as last viewed by the user (if logged in) at
    the current time.
    """
    now = datetime.now()

    last_view = find_last_category_view(user_id, category_id)

    if last_view is not None:
        last_view.occurred_at = now
    else:
        last_view = LastCategoryView(user_id, category_id, now)
        db.session.add(last_view)

    db.session.commit()


# -------------------------------------------------------------------- #
# topics


def contains_topic_unseen_postings(topic: Topic, user_id: UserID) -> bool:
    """Return `True` if the topic contains postings created after the
    last time the user viewed it.
    """
    last_viewed_at = find_topic_last_viewed_at(topic.id, user_id)

    return last_viewed_at is None \
        or topic.last_updated_at > last_viewed_at


def find_last_topic_view(user_id: UserID, topic_id: TopicID
                        ) -> Optional[LastTopicView]:
    """Return the user's last view of the topic, or `None` if not found."""
    return LastTopicView.query \
        .filter_by(user_id=user_id, topic_id=topic_id) \
        .first()


def find_topic_last_viewed_at(topic_id: TopicID, user_id: UserID
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
    now = datetime.now()

    last_view = find_last_topic_view(user_id, topic_id)

    if last_view is not None:
        last_view.occurred_at = now
    else:
        last_view = LastTopicView(user_id, topic_id, now)
        db.session.add(last_view)

    db.session.commit()


# -------------------------------------------------------------------- #


def mark_all_topics_in_category_as_viewed(category_id: CategoryID,
                                          user_id: UserID) -> None:
    """Mark all topics in the category as viewed."""
    topic_ids = topic_service.get_all_topic_ids_in_category(category_id)

    if not topic_ids:
        return

    now = datetime.now()

    # Fetch existing last views.
    last_views = LastTopicView.query \
        .filter_by(user_id=user_id) \
        .filter(LastTopicView.topic_id.in_(topic_ids)) \
        .all()

    # Update existing last views.
    for last_view in last_views:
        last_view.occurred_at = now

    # Create last views for remaining topics.
    last_view_topic_ids = {last_view.topic_id for last_view in last_views}
    remaining_topic_ids = topic_ids - last_view_topic_ids
    for topic_id in remaining_topic_ids:
        last_view = LastTopicView(user_id, topic_id, now)
        db.session.add(last_view)

    db.session.commit()
