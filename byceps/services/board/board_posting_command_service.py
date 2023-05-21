"""
byceps.services.board.board_posting_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete

from byceps.database import db
from byceps.events.board import (
    BoardPostingCreatedEvent,
    BoardPostingHiddenEvent,
    BoardPostingUnhiddenEvent,
    BoardPostingUpdatedEvent,
)
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import UserID

from . import (
    board_aggregation_service,
    board_posting_query_service,
    board_topic_query_service,
)
from .dbmodels.posting import DbPosting
from .models import PostingID, TopicID


def create_posting(
    topic_id: TopicID, creator_id: UserID, body: str
) -> tuple[DbPosting, BoardPostingCreatedEvent]:
    """Create a posting in that topic."""
    topic = board_topic_query_service.get_topic(topic_id)
    creator = _get_user(creator_id)

    db_posting = DbPosting(topic, creator.id, body)
    db.session.add(db_posting)
    db.session.commit()

    board_aggregation_service.aggregate_topic(topic)

    event = BoardPostingCreatedEvent(
        occurred_at=db_posting.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        board_id=topic.category.board_id,
        posting_id=db_posting.id,
        posting_creator_id=creator.id,
        posting_creator_screen_name=creator.screen_name,
        topic_id=topic.id,
        topic_title=topic.title,
        topic_muted=topic.muted,
        url=None,
    )

    return db_posting, event


def update_posting(
    posting_id: PostingID, editor_id: UserID, body: str, *, commit: bool = True
) -> BoardPostingUpdatedEvent:
    """Update the posting."""
    db_posting = _get_posting(posting_id)
    editor = _get_user(editor_id)

    now = datetime.utcnow()

    db_posting.body = body.strip()
    db_posting.last_edited_at = now
    db_posting.last_edited_by_id = editor.id
    db_posting.edit_count += 1

    if commit:
        db.session.commit()

    posting_creator = _get_user(db_posting.creator_id)
    return BoardPostingUpdatedEvent(
        occurred_at=now,
        initiator_id=editor.id,
        initiator_screen_name=editor.screen_name,
        board_id=db_posting.topic.category.board_id,
        posting_id=db_posting.id,
        posting_creator_id=posting_creator.id,
        posting_creator_screen_name=posting_creator.screen_name,
        topic_id=db_posting.topic.id,
        topic_title=db_posting.topic.title,
        editor_id=editor.id,
        editor_screen_name=editor.screen_name,
        url=None,
    )


def hide_posting(
    posting_id: PostingID, moderator_id: UserID
) -> BoardPostingHiddenEvent:
    """Hide the posting."""
    db_posting = _get_posting(posting_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    db_posting.hidden = True
    db_posting.hidden_at = now
    db_posting.hidden_by_id = moderator.id
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_posting.topic)

    posting_creator = _get_user(db_posting.creator_id)
    event = BoardPostingHiddenEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=db_posting.topic.category.board_id,
        posting_id=db_posting.id,
        posting_creator_id=posting_creator.id,
        posting_creator_screen_name=posting_creator.screen_name,
        topic_id=db_posting.topic.id,
        topic_title=db_posting.topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )

    return event


def unhide_posting(
    posting_id: PostingID, moderator_id: UserID
) -> BoardPostingUnhiddenEvent:
    """Un-hide the posting."""
    db_posting = _get_posting(posting_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    # TODO: Store who un-hid the posting.
    db_posting.hidden = False
    db_posting.hidden_at = None
    db_posting.hidden_by_id = None
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_posting.topic)

    posting_creator = _get_user(db_posting.creator_id)
    event = BoardPostingUnhiddenEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=db_posting.topic.category.board_id,
        posting_id=db_posting.id,
        posting_creator_id=posting_creator.id,
        posting_creator_screen_name=posting_creator.screen_name,
        topic_id=db_posting.topic.id,
        topic_title=db_posting.topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )

    return event


def delete_posting(posting_id: PostingID) -> None:
    """Delete a posting."""
    db.session.execute(delete(DbPosting).filter_by(id=posting_id))
    db.session.commit()


def _get_posting(posting_id: PostingID) -> DbPosting:
    return board_posting_query_service.get_posting(posting_id)


def _get_user(user_id: UserID) -> User:
    return user_service.get_user(user_id)
