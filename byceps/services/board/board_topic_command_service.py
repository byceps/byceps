"""
byceps.services.board.board_topic_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete

from byceps.database import db
from byceps.events.base import EventBrand, EventUser
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
from byceps.services.user.models.user import User, UserID
from byceps.util.uuid import generate_uuid7

from . import (
    board_aggregation_service,
    board_posting_command_service,
    board_topic_query_service,
)
from .dbmodels.category import DbBoardCategory
from .dbmodels.posting import DbInitialTopicPostingAssociation, DbPosting
from .dbmodels.topic import DbTopic
from .models import BoardCategoryID, PostingID, Topic, TopicID


def create_topic(
    category_id: BoardCategoryID, creator: User, title: str, body: str
) -> tuple[Topic, BoardTopicCreatedEvent]:
    """Create a topic with an initial posting in that category."""
    topic_id = TopicID(generate_uuid7())
    posting_id = PostingID(generate_uuid7())

    db_topic = DbTopic(topic_id, category_id, creator.id, title)
    db_posting = DbPosting(posting_id, topic_id, creator.id, body)
    db_initial_topic_posting_association = DbInitialTopicPostingAssociation(
        topic_id, posting_id
    )

    db.session.add(db_topic)
    db.session.add(db_posting)
    db.session.add(db_initial_topic_posting_association)
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_topic)

    db_category = db_topic.category
    brand = brand_service.get_brand(db_category.board.brand_id)
    topic = board_topic_query_service._db_entity_to_topic(db_topic)

    event = BoardTopicCreatedEvent(
        occurred_at=topic.created_at,
        initiator=EventUser.from_user(creator),
        brand=EventBrand.from_brand(brand),
        board_id=db_category.board_id,
        topic_id=topic.id,
        topic_creator=EventUser.from_user(creator),
        topic_title=topic.title,
        url=None,
    )

    return topic, event


def update_topic(
    topic_id: TopicID, editor: User, title: str, body: str
) -> BoardTopicUpdatedEvent:
    """Update the topic (and its initial posting)."""
    db_topic = _get_db_topic(topic_id)

    db_topic.title = title.strip()

    posting_event = board_posting_command_service.update_posting(
        db_topic.initial_posting.id, editor, body, commit=False
    )

    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicUpdatedEvent(
        occurred_at=posting_event.occurred_at,
        initiator=EventUser.from_user(editor),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        editor=EventUser.from_user(editor),
        url=None,
    )


def hide_topic(topic_id: TopicID, moderator: User) -> BoardTopicHiddenEvent:
    """Hide the topic."""
    db_topic = _get_db_topic(topic_id)

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
        initiator=EventUser.from_user(moderator),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        moderator=EventUser.from_user(moderator),
        url=None,
    )


def unhide_topic(topic_id: TopicID, moderator: User) -> BoardTopicUnhiddenEvent:
    """Un-hide the topic."""
    db_topic = _get_db_topic(topic_id)

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
        initiator=EventUser.from_user(moderator),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        moderator=EventUser.from_user(moderator),
        url=None,
    )


def lock_topic(topic_id: TopicID, moderator: User) -> BoardTopicLockedEvent:
    """Lock the topic."""
    db_topic = _get_db_topic(topic_id)

    now = datetime.utcnow()

    db_topic.locked = True
    db_topic.locked_at = now
    db_topic.locked_by_id = moderator.id
    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicLockedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        moderator=EventUser.from_user(moderator),
        url=None,
    )


def unlock_topic(topic_id: TopicID, moderator: User) -> BoardTopicUnlockedEvent:
    """Unlock the topic."""
    db_topic = _get_db_topic(topic_id)

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
        initiator=EventUser.from_user(moderator),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        moderator=EventUser.from_user(moderator),
        url=None,
    )


def pin_topic(topic_id: TopicID, moderator: User) -> BoardTopicPinnedEvent:
    """Pin the topic."""
    db_topic = _get_db_topic(topic_id)

    now = datetime.utcnow()

    db_topic.pinned = True
    db_topic.pinned_at = now
    db_topic.pinned_by_id = moderator.id
    db.session.commit()

    brand = brand_service.get_brand(db_topic.category.board.brand_id)
    topic_creator = _get_user(db_topic.creator_id)
    return BoardTopicPinnedEvent(
        occurred_at=now,
        initiator=EventUser.from_user(moderator),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        moderator=EventUser.from_user(moderator),
        url=None,
    )


def unpin_topic(topic_id: TopicID, moderator: User) -> BoardTopicUnpinnedEvent:
    """Unpin the topic."""
    db_topic = _get_db_topic(topic_id)

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
        initiator=EventUser.from_user(moderator),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        moderator=EventUser.from_user(moderator),
        url=None,
    )


def move_topic(
    topic_id: TopicID, new_category_id: BoardCategoryID, moderator: User
) -> BoardTopicMovedEvent:
    """Move the topic to another category."""
    db_topic = _get_db_topic(topic_id)

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
        initiator=EventUser.from_user(moderator),
        brand=EventBrand.from_brand(brand),
        board_id=db_topic.category.board_id,
        topic_id=db_topic.id,
        topic_creator=EventUser.from_user(topic_creator),
        topic_title=db_topic.title,
        old_category_id=db_old_category.id,
        old_category_title=db_old_category.title,
        new_category_id=db_new_category.id,
        new_category_title=db_new_category.title,
        moderator=EventUser.from_user(moderator),
        url=None,
    )


def limit_topic_to_announcements(topic_id: TopicID) -> None:
    """Limit posting in the topic to moderators."""
    db_topic = _get_db_topic(topic_id)

    db_topic.posting_limited_to_moderators = True
    db.session.commit()


def remove_limit_of_topic_to_announcements(topic_id: TopicID) -> None:
    """Allow non-moderators to post in the topic again."""
    db_topic = _get_db_topic(topic_id)

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


def _get_db_topic(topic_id: TopicID) -> DbTopic:
    return board_topic_query_service.get_db_topic(topic_id)


def _get_user(user_id: UserID) -> User:
    return user_service.get_user(user_id)
