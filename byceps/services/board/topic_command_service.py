"""
byceps.services.board.topic_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Tuple

from ...database import db
from ...events.board import (
    BoardTopicCreated,
    BoardTopicHidden,
    BoardTopicLocked,
    BoardTopicMoved,
    BoardTopicPinned,
    BoardTopicUnhidden,
    BoardTopicUnlocked,
    BoardTopicUnpinned,
    BoardTopicUpdated,
)
from ...typing import UserID

from .aggregation_service import aggregate_category, aggregate_topic
from .models.category import Category as DbCategory
from .models.posting import InitialTopicPostingAssociation, Posting as DbPosting
from .models.topic import Topic as DbTopic
from .posting_command_service import update_posting
from . import topic_query_service
from .transfer.models import CategoryID, TopicID


def create_topic(
    category_id: CategoryID, creator_id: UserID, title: str, body: str
) -> Tuple[DbTopic, BoardTopicCreated]:
    """Create a topic with an initial posting in that category."""
    topic = DbTopic(category_id, creator_id, title)
    posting = DbPosting(topic, creator_id, body)
    initial_topic_posting_association = InitialTopicPostingAssociation(
        topic, posting
    )

    db.session.add(topic)
    db.session.add(posting)
    db.session.add(initial_topic_posting_association)
    db.session.commit()

    aggregate_topic(topic)

    event = BoardTopicCreated(
        occurred_at=topic.created_at, topic_id=topic.id, url=None
    )

    return topic, event


def update_topic(
    topic_id: TopicID, editor_id: UserID, title: str, body: str
) -> BoardTopicUpdated:
    """Update the topic (and its initial posting)."""
    topic = _get_topic(topic_id)

    topic.title = title.strip()

    posting_event = update_posting(
        topic.initial_posting.id, editor_id, body, commit=False
    )

    db.session.commit()

    return BoardTopicUpdated(
        occurred_at=posting_event.occurred_at,
        topic_id=topic.id,
        editor_id=editor_id,
        url=None,
    )


def hide_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicHidden:
    """Hide the topic."""
    topic = _get_topic(topic_id)

    now = datetime.utcnow()

    topic.hidden = True
    topic.hidden_at = now
    topic.hidden_by_id = moderator_id
    db.session.commit()

    aggregate_topic(topic)

    return BoardTopicHidden(
        occurred_at=now, topic_id=topic.id, moderator_id=moderator_id, url=None
    )


def unhide_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicUnhidden:
    """Un-hide the topic."""
    topic = _get_topic(topic_id)

    now = datetime.utcnow()

    # TODO: Store who un-hid the topic.
    topic.hidden = False
    topic.hidden_at = None
    topic.hidden_by_id = None
    db.session.commit()

    aggregate_topic(topic)

    return BoardTopicUnhidden(
        occurred_at=now, topic_id=topic.id, moderator_id=moderator_id, url=None
    )


def lock_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicLocked:
    """Lock the topic."""
    topic = _get_topic(topic_id)

    now = datetime.utcnow()

    topic.locked = True
    topic.locked_at = now
    topic.locked_by_id = moderator_id
    db.session.commit()

    return BoardTopicLocked(
        occurred_at=now, topic_id=topic.id, moderator_id=moderator_id, url=None
    )


def unlock_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicUnlocked:
    """Unlock the topic."""
    topic = _get_topic(topic_id)

    now = datetime.utcnow()

    # TODO: Store who unlocked the topic.
    topic.locked = False
    topic.locked_at = None
    topic.locked_by_id = None
    db.session.commit()

    return BoardTopicUnlocked(
        occurred_at=now, topic_id=topic.id, moderator_id=moderator_id, url=None
    )


def pin_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicPinned:
    """Pin the topic."""
    topic = _get_topic(topic_id)

    now = datetime.utcnow()

    topic.pinned = True
    topic.pinned_at = now
    topic.pinned_by_id = moderator_id
    db.session.commit()

    return BoardTopicPinned(
        occurred_at=now, topic_id=topic.id, moderator_id=moderator_id, url=None
    )


def unpin_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicUnpinned:
    """Unpin the topic."""
    topic = _get_topic(topic_id)

    now = datetime.utcnow()

    # TODO: Store who unpinned the topic.
    topic.pinned = False
    topic.pinned_at = None
    topic.pinned_by_id = None
    db.session.commit()

    return BoardTopicUnpinned(
        occurred_at=now, topic_id=topic.id, moderator_id=moderator_id, url=None
    )


def move_topic(
    topic_id: TopicID, new_category_id: CategoryID, moderator_id: UserID
) -> BoardTopicMoved:
    """Move the topic to another category."""
    topic = _get_topic(topic_id)

    now = datetime.utcnow()

    old_category = topic.category
    new_category = DbCategory.query.get(new_category_id)

    topic.category = new_category
    db.session.commit()

    for category in old_category, new_category:
        aggregate_category(category)

    return BoardTopicMoved(
        occurred_at=now,
        topic_id=topic.id,
        old_category_id=old_category.id,
        new_category_id=new_category.id,
        moderator_id=moderator_id,
        url=None,
    )


def limit_topic_to_announcements(topic_id: TopicID) -> None:
    """Limit posting in the topic to moderators."""
    topic = _get_topic(topic_id)

    topic.posting_limited_to_moderators = True
    db.session.commit()


def remove_limit_of_topic_to_announcements(topic_id: TopicID) -> None:
    """Allow non-moderators to post in the topic again."""
    topic = _get_topic(topic_id)

    topic.posting_limited_to_moderators = False
    db.session.commit()


def _get_topic(topic_id: TopicID) -> DbTopic:
    return topic_query_service.get_topic(topic_id)
