"""
byceps.services.board.topic_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ...database import db
from ...typing import UserID

from .aggregation_service import aggregate_category, aggregate_topic
from .models.category import Category as DbCategory
from .models.posting import InitialTopicPostingAssociation, Posting as DbPosting
from .models.topic import Topic as DbTopic
from .posting_command_service import update_posting
from .transfer.models import CategoryID


def create_topic(
    category_id: CategoryID, creator_id: UserID, title: str, body: str
) -> DbTopic:
    """Create a topic with an initial posting in that category."""
    topic = DbTopic(category_id, creator_id, title)
    posting = DbPosting(topic, creator_id, body)
    initial_topic_posting_association = InitialTopicPostingAssociation(topic,
                                                                       posting)

    db.session.add(topic)
    db.session.add(posting)
    db.session.add(initial_topic_posting_association)
    db.session.commit()

    aggregate_topic(topic)

    return topic


def update_topic(
    topic: DbTopic, editor_id: UserID, title: str, body: str
) -> None:
    """Update the topic (and its initial posting)."""
    topic.title = title.strip()

    update_posting(topic.initial_posting, editor_id, body, commit=False)

    db.session.commit()


def hide_topic(topic: DbTopic, hidden_by_id: UserID) -> None:
    """Hide the topic."""
    topic.hidden = True
    topic.hidden_at = datetime.utcnow()
    topic.hidden_by_id = hidden_by_id
    db.session.commit()

    aggregate_topic(topic)


def unhide_topic(topic: DbTopic, unhidden_by_id: UserID) -> None:
    """Un-hide the topic."""
    # TODO: Store who un-hid the topic.
    topic.hidden = False
    topic.hidden_at = None
    topic.hidden_by_id = None
    db.session.commit()

    aggregate_topic(topic)


def lock_topic(topic: DbTopic, locked_by_id: UserID) -> None:
    """Lock the topic."""
    topic.locked = True
    topic.locked_at = datetime.utcnow()
    topic.locked_by_id = locked_by_id
    db.session.commit()


def unlock_topic(topic: DbTopic, unlocked_by_id: UserID) -> None:
    """Unlock the topic."""
    # TODO: Store who unlocked the topic.
    topic.locked = False
    topic.locked_at = None
    topic.locked_by_id = None
    db.session.commit()


def pin_topic(topic: DbTopic, pinned_by_id: UserID) -> None:
    """Pin the topic."""
    topic.pinned = True
    topic.pinned_at = datetime.utcnow()
    topic.pinned_by_id = pinned_by_id
    db.session.commit()


def unpin_topic(topic: DbTopic, unpinned_by_id: UserID) -> None:
    """Unpin the topic."""
    # TODO: Store who unpinned the topic.
    topic.pinned = False
    topic.pinned_at = None
    topic.pinned_by_id = None
    db.session.commit()


def move_topic(topic: DbTopic, new_category_id: CategoryID) -> None:
    """Move the topic to another category."""
    old_category = topic.category
    new_category = DbCategory.query.get(new_category_id)

    topic.category = new_category
    db.session.commit()

    for category in old_category, new_category:
        aggregate_category(category)


def limit_topic_to_announcements(topic: DbTopic) -> None:
    """Limit posting in the topic to moderators."""
    topic.posting_limited_to_moderators = True
    db.session.commit()


def remove_limit_of_topic_to_announcements(topic: DbTopic) -> None:
    """Allow non-moderators to post in the topic again."""
    topic.posting_limited_to_moderators = False
    db.session.commit()
