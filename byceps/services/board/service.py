"""
byceps.services.board.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ...database import db

from ..user.models.user import User

from .models.category import Category, LastCategoryView
from .models.topic import LastTopicView, Topic


# -------------------------------------------------------------------- #
# last views


def mark_category_as_just_viewed(category: Category, user: User) -> None:
    """Mark the category as last viewed by the user (if logged in) at
    the current time.
    """
    if user.is_anonymous:
        return

    last_view = LastCategoryView.find(user, category)
    if last_view is None:
        last_view = LastCategoryView(user.id, category.id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()


def mark_topic_as_just_viewed(topic: Topic, user: User) -> None:
    """Mark the topic as last viewed by the user (if logged in) at the
    current time.
    """
    if user.is_anonymous:
        return

    last_view = LastTopicView.find(user, topic)
    if last_view is None:
        last_view = LastTopicView(user.id, topic.id)
        db.session.add(last_view)

    last_view.occured_at = datetime.now()
    db.session.commit()
