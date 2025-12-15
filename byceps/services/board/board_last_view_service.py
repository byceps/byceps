"""
byceps.services.board.board_last_view_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.services.user.models.user import UserID

from .dbmodels.topic import DbTopic, DbLastTopicView
from .models import TopicID


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
