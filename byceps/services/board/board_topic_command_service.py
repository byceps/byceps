"""
byceps.services.board.board_topic_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete

from byceps.database import db
from byceps.events.board import (
    BoardTopicCreatedEvent,
    BoardTopicHiddenEvent,
    BoardTopicLockedEvent,
    BoardTopicMovedEvent,
    BoardTopicPinnedEvent,
    BoardTopicUnhiddenEvent,
    BoardTopicUnlockedEvent,
    BoardTopicUnpinnedEvent,
    BoardTopicUpdatedEvent,
)
from byceps.services.brand import brand_service
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import UserID

from . import (
    board_aggregation_service,
    board_posting_command_service,
    board_topic_query_service,
)
from .dbmodels.category import DbBoardCategory
from .dbmodels.posting import DbInitialTopicPostingAssociation, DbPosting
from .dbmodels.topic import DbTopic
from .models import BoardCategoryID, TopicID


def create_topic(
    category_id: BoardCategoryID, creator: User, title: str, body: str
) -> tuple[DbTopic, BoardTopicCreatedEvent]:
    """Create a topic with an initial posting in that category."""
    db_topic = DbTopic(category_id, creator.id, title)
    db_posting = DbPosting(db_topic, creator.id, body)
    db_initial_topic_posting_association = DbInitialTopicPostingAssociation(
        db_topic, db_posting
    )

    db.session.add(db_topic)
    db.session.add(db_posting)
    db.session.add(db_initial_topic_posting_association)
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_topic)

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    event = BoardTopicCreatedEvent(
        occurred_at=db_topic.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=creator.id,
        topic_creator_screen_name=creator.screen_name,
        topic_title=db_topic.title,
        url=None,
    )

    return db_topic, event


def update_topic(
    topic_id: TopicID, editor: User, title: str, body: str
) -> BoardTopicUpdatedEvent:
    """Update the topic (and its initial posting)."""
    db_topic = _get_topic(topic_id)

    db_topic.title = title.strip()

    posting_event = board_posting_command_service.update_posting(
        db_topic.initial_posting.id, editor, body, commit=False
    )

    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicUpdatedEvent(
        occurred_at=posting_event.occurred_at,
        initiator_id=editor.id,
        initiator_screen_name=editor.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        editor_id=editor.id,
        editor_screen_name=editor.screen_name,
        url=None,
    )


def hide_topic(topic_id: TopicID, moderator: User) -> BoardTopicHiddenEvent:
    """Hide the topic."""
    db_topic = _get_topic(topic_id)

    now = datetime.utcnow()

    db_topic.hidden = True
    db_topic.hidden_at = now
    db_topic.hidden_by_id = moderator.id
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_topic)

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicHiddenEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def unhide_topic(topic_id: TopicID, moderator: User) -> BoardTopicUnhiddenEvent:
    """Un-hide the topic."""
    db_topic = _get_topic(topic_id)

    now = datetime.utcnow()

    # TODO: Store who un-hid the topic.
    db_topic.hidden = False
    db_topic.hidden_at = None
    db_topic.hidden_by_id = None
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_topic)

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicUnhiddenEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def lock_topic(topic_id: TopicID, moderator: User) -> BoardTopicLockedEvent:
    """Lock the topic."""
    db_topic = _get_topic(topic_id)

    now = datetime.utcnow()

    db_topic.locked = True
    db_topic.locked_at = now
    db_topic.locked_by_id = moderator.id
    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicLockedEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def unlock_topic(topic_id: TopicID, moderator: User) -> BoardTopicUnlockedEvent:
    """Unlock the topic."""
    db_topic = _get_topic(topic_id)

    now = datetime.utcnow()

    # TODO: Store who unlocked the topic.
    db_topic.locked = False
    db_topic.locked_at = None
    db_topic.locked_by_id = None
    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicUnlockedEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def pin_topic(topic_id: TopicID, moderator: User) -> BoardTopicPinnedEvent:
    """Pin the topic."""
    db_topic = _get_topic(topic_id)

    now = datetime.utcnow()

    db_topic.pinned = True
    db_topic.pinned_at = now
    db_topic.pinned_by_id = moderator.id
    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicPinnedEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def unpin_topic(topic_id: TopicID, moderator: User) -> BoardTopicUnpinnedEvent:
    """Unpin the topic."""
    db_topic = _get_topic(topic_id)

    now = datetime.utcnow()

    # TODO: Store who unpinned the topic.
    db_topic.pinned = False
    db_topic.pinned_at = None
    db_topic.pinned_by_id = None
    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicUnpinnedEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def move_topic(
    topic_id: TopicID, new_category_id: BoardCategoryID, moderator: User
) -> BoardTopicMovedEvent:
    """Move the topic to another category."""
    db_topic = _get_topic(topic_id)

    now = datetime.utcnow()

    db_old_category = db_topic.category
    db_new_category = db.session.get(DbBoardCategory, new_category_id)

    db_topic.category = db_new_category
    db.session.commit()

    for db_category in db_old_category, db_new_category:
        board_aggregation_service.aggregate_category(db_category)

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicMovedEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator_id=topic_creator.id,
        topic_creator_screen_name=topic_creator.screen_name,
        topic_title=db_topic.title,
        old_category_id=db_old_category.id,
        old_category_title=db_old_category.title,
        new_category_id=db_new_category.id,
        new_category_title=db_new_category.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )


def limit_topic_to_announcements(topic_id: TopicID) -> None:
    """Limit posting in the topic to moderators."""
    db_topic = _get_topic(topic_id)

    db_topic.posting_limited_to_moderators = True
    db.session.commit()


def remove_limit_of_topic_to_announcements(topic_id: TopicID) -> None:
    """Allow non-moderators to post in the topic again."""
    db_topic = _get_topic(topic_id)

    db_topic.posting_limited_to_moderators = False
    db.session.commit()


def delete_topic(topic_id: TopicID) -> None:
    """Delete a topic."""
    db.session.execute(
        delete(DbInitialTopicPostingAssociation).filter_by(topic_id=topic_id)
    )
    db.session.execute(delete(DbPosting).filter_by(topic_id=topic_id))
    db.session.execute(delete(DbTopic).filter_by(id=topic_id))
    db.session.commit()


def _get_topic(topic_id: TopicID) -> DbTopic:
    return board_topic_query_service.get_topic(topic_id)


def _get_user(user_id: UserID) -> User:
    return user_service.get_user(user_id)
