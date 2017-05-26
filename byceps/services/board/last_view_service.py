"""
byceps.services.board.last_view_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ...database import db

from ..user.models.user import User

from .models.category import CategoryID, LastCategoryView
from .models.topic import LastTopicView, TopicID


def mark_category_as_just_viewed(category_id: CategoryID, user: User) -> None:
    """Mark the category as last viewed by the user (if logged in) at
    the current time.
    """
    if user.is_anonymous:
        return

    last_view = LastCategoryView.find(user, category_id)
    if last_view is None:
        last_view = LastCategoryView(user.id, category_id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()


def mark_topic_as_just_viewed(topic_id: TopicID, user: User) -> None:
    """Mark the topic as last viewed by the user (if logged in) at the
    current time.
    """
    if user.is_anonymous:
        return

    last_view = LastTopicView.find(user, topic_id)
    if last_view is None:
        last_view = LastTopicView(user.id, topic_id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()
