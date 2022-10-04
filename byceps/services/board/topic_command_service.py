"""
byceps.services.board.topic_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime

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

from ..user import user_service
from ..user.transfer.models import User

from .aggregation_service import aggregate_category, aggregate_topic
from .dbmodels.category import DbCategory
from .dbmodels.posting import DbInitialTopicPostingAssociation, DbPosting
from .dbmodels.topic import DbTopic
from .posting_command_service import update_posting
from . import topic_query_service
from .transfer.models import CategoryID, TopicID


def create_topic(
    category_id: CategoryID, creator_id: UserID, title: str, body: str
) -> tuple[DbTopic, BoardTopicCreated]:
    """Create a topic with an initial posting in that category."""
    creator = _get_user(creator_id)

    topic = DbTopic(category_id, creator.id, title)
    posting = DbPosting(topic, creator.id, body)
    initial_topic_posting_association = DbInitialTopicPostingAssociation(
        topic, posting
    )

    db.session.add(topic)
    db.session.add(posting)
    db.session.add(initial_topic_posting_association)
    db.session.commit()

    aggregate_topic(topic)

    event = BoardTopicCreated(
        occurred_at=topic.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=creator.id,
        topic_creator_screen_name=creator.screen_name,
        topic_title=topic.title,
        url=None,
    )

    return topic, event


def update_topic(
    topic_id: TopicID, editor_id: UserID, title: str, body: str
) -> BoardTopicUpdated:
    """Update the topic (and its initial posting)."""
    topic = _get_topic(topic_id)
    editor = _get_user(editor_id)

    topic.title = title.strip()

    posting_event = update_posting(
        topic.initial_posting.id, editor.id, body, commit=False
    )

    db.session.commit()

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicUpdated(
        occurred_at=posting_event.occurred_at,
        initiator_id=editor.id,
        initiator_screen_name=editor.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        editor_id=editor.id,
        editor_screen_name=editor.screen_name,
        url=None,
    )


def hide_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicHidden:
    """Hide the topic."""
    topic = _get_topic(topic_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    topic.hidden = True
    topic.hidden_at = now
    topic.hidden_by_id = moderator.id
    db.session.commit()

    aggregate_topic(topic)

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicHidden(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def unhide_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicUnhidden:
    """Un-hide the topic."""
    topic = _get_topic(topic_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    # TODO: Store who un-hid the topic.
    topic.hidden = False
    topic.hidden_at = None
    topic.hidden_by_id = None
    db.session.commit()

    aggregate_topic(topic)

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicUnhidden(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def lock_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicLocked:
    """Lock the topic."""
    topic = _get_topic(topic_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    topic.locked = True
    topic.locked_at = now
    topic.locked_by_id = moderator.id
    db.session.commit()

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicLocked(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def unlock_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicUnlocked:
    """Unlock the topic."""
    topic = _get_topic(topic_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    # TODO: Store who unlocked the topic.
    topic.locked = False
    topic.locked_at = None
    topic.locked_by_id = None
    db.session.commit()

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicUnlocked(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def pin_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicPinned:
    """Pin the topic."""
    topic = _get_topic(topic_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    topic.pinned = True
    topic.pinned_at = now
    topic.pinned_by_id = moderator.id
    db.session.commit()

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicPinned(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def unpin_topic(topic_id: TopicID, moderator_id: UserID) -> BoardTopicUnpinned:
    """Unpin the topic."""
    topic = _get_topic(topic_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    # TODO: Store who unpinned the topic.
    topic.pinned = False
    topic.pinned_at = None
    topic.pinned_by_id = None
    db.session.commit()

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicUnpinned(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def move_topic(
    topic_id: TopicID, new_category_id: CategoryID, moderator_id: UserID
) -> BoardTopicMoved:
    """Move the topic to another category."""
    topic = _get_topic(topic_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    old_category = topic.category
    new_category = db.session.get(DbCategory, new_category_id)

    topic.category = new_category
    db.session.commit()

    for category in old_category, new_category:
        aggregate_category(category)

    topic_creator = _get_user(topic.creator_id)
    return BoardTopicMoved(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=topic.category.board_id,
        topic_id=topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=topic.title,
        old_category_id=old_category.id,
        old_category_title=old_category.title,
        new_category_id=new_category.id,
        new_category_title=new_category.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
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


def delete_topic(topic_id: TopicID) -> None:
    """Delete a topic."""
    db.session.query(DbInitialTopicPostingAssociation) \
        .filter_by(topic_id=topic_id) \
        .delete()

    db.session.query(DbPosting) \
        .filter_by(topic_id=topic_id) \
        .delete()

    db.session.query(DbTopic) \
        .filter_by(id=topic_id) \
        .delete()

    db.session.commit()


def _get_topic(topic_id: TopicID) -> DbTopic:
    return topic_query_service.get_topic(topic_id)


def _get_user(user_id: UserID) -> User:
    return user_service.get_user(user_id)
