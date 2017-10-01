"""
byceps.services.board.last_view_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from ...database import db
from ...typing import UserID

from .models.category import Category, CategoryID, LastCategoryView
from .models.topic import LastTopicView, Topic, TopicID


# -------------------------------------------------------------------- #
# categories


def contains_category_unseen_postings(category: Category, user_id: UserID
                                     ) -> bool:
    """Return `True` if the category contains postings created after the
    last time the user viewed it.
    """
    if category.last_posting_updated_at is None:
        return False

    last_view = LastCategoryView.find(user_id, category.id)

    if last_view is None:
        return True

    return category.last_posting_updated_at > last_view.occured_at


def mark_category_as_just_viewed(category_id: CategoryID, user_id: UserID
                                ) -> None:
    """Mark the category as last viewed by the user (if logged in) at
    the current time.
    """
    last_view = LastCategoryView.find(user_id, category_id)
    if last_view is None:
        last_view = LastCategoryView(user_id, category_id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
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


def find_topic_last_viewed_at(topic_id: TopicID, user_id: UserID
                             ) -> Optional[datetime]:
    """Return the time the topic was last viewed by the user (or
    nothing, if it hasn't been viewed by the user yet).
    """
    last_view = LastTopicView.find(user_id, topic_id)
    return last_view.occured_at if (last_view is not None) else None


def mark_topic_as_just_viewed(topic_id: TopicID, user_id: UserID) -> None:
    """Mark the topic as last viewed by the user (if logged in) at the
    current time.
    """
    last_view = LastTopicView.find(user_id, topic_id)
    if last_view is None:
        last_view = LastTopicView(user_id, topic_id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()
