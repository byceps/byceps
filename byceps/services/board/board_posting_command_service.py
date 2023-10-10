"""
byceps.services.board.board_posting_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.events.board import (
    BoardPostingCreatedEvent,
    BoardPostingHiddenEvent,
    BoardPostingUnhiddenEvent,
    BoardPostingUpdatedEvent,
)
from byceps.services.brand import brand_service
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from . import (
    board_aggregation_service,
    board_posting_query_service,
    board_topic_query_service,
)
from .dbmodels.posting import DbPosting, DbPostingReaction
from .models import PostingID, TopicID


def create_posting(
    topic_id: TopicID, creator: User, body: str
) -> tuple[DbPosting, BoardPostingCreatedEvent]:
    """Create a posting in that topic."""
    topic = board_topic_query_service.get_topic(topic_id)

    db_posting = DbPosting(topic, creator.id, body)
    db.session.add(db_posting)
    db.session.commit()

    board_aggregation_service.aggregate_topic(topic)

    brand = brand_service.get_brand(db_posting.topic.category.board.brand_id)
    event = BoardPostingCreatedEvent(
        occurred_at=db_posting.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
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
    posting_id: PostingID, editor: User, body: str, *, commit: bool = True
) -> BoardPostingUpdatedEvent:
    """Update the posting."""
    db_posting = _get_posting(posting_id)

    now = datetime.utcnow()

    db_posting.body = body.strip()
    db_posting.last_edited_at = now
    db_posting.last_edited_by_id = editor.id
    db_posting.edit_count += 1

    if commit:
        db.session.commit()

    brand = brand_service.get_brand(db_posting.topic.category.board.brand_id)
    posting_creator = _get_user(db_posting.creator_id)
    return BoardPostingUpdatedEvent(
        occurred_at=now,
        initiator_id=editor.id,
        initiator_screen_name=editor.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
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
    posting_id: PostingID, moderator: User
) -> BoardPostingHiddenEvent:
    """Hide the posting."""
    db_posting = _get_posting(posting_id)

    now = datetime.utcnow()

    db_posting.hidden = True
    db_posting.hidden_at = now
    db_posting.hidden_by_id = moderator.id
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_posting.topic)

    brand = brand_service.get_brand(db_posting.topic.category.board.brand_id)
    posting_creator = _get_user(db_posting.creator_id)
    event = BoardPostingHiddenEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
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
    posting_id: PostingID, moderator: User
) -> BoardPostingUnhiddenEvent:
    """Un-hide the posting."""
    db_posting = _get_posting(posting_id)

    now = datetime.utcnow()

    # TODO: Store who un-hid the posting.
    db_posting.hidden = False
    db_posting.hidden_at = None
    db_posting.hidden_by_id = None
    db.session.commit()

    board_aggregation_service.aggregate_topic(db_posting.topic)

    brand = brand_service.get_brand(db_posting.topic.category.board.brand_id)
    posting_creator = _get_user(db_posting.creator_id)
    event = BoardPostingUnhiddenEvent(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        brand_id=brand.id,
        brand_title=brand.title,
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


def add_reaction(
    posting_id: PostingID, user: User, kind: str
) -> Result[None, None]:
    """Add user reaction to the posting."""
    reaction_exists = _is_reaction_existing(posting_id, user.id, kind)
    if reaction_exists:
        return Err(None)

    reaction_id = generate_uuid7()
    created_at = datetime.utcnow()

    db_reaction = DbPostingReaction(
        reaction_id, created_at, posting_id, user.id, kind
    )
    db.session.add(db_reaction)
    db.session.commit()

    return Ok(None)


def remove_reaction(
    posting_id: PostingID, user: User, kind: str
) -> Result[None, None]:
    """Remove user reaction from the posting."""
    reaction_exists = _is_reaction_existing(posting_id, user.id, kind)
    if not reaction_exists:
        return Err(None)

    db.session.execute(
        delete(DbPostingReaction)
        .filter_by(posting_id=posting_id)
        .filter_by(user_id=user.id)
        .filter_by(kind=kind)
    )
    db.session.commit()

    return Ok(None)


def _is_reaction_existing(
    posting_id: PostingID, user_id: UserID, kind: str
) -> bool:
    return db.session.scalar(
        select(
            select(DbPostingReaction)
            .filter_by(posting_id=posting_id)
            .filter_by(user_id=user_id)
            .filter_by(kind=kind)
            .exists()
        )
    )


def _get_posting(posting_id: PostingID) -> DbPosting:
    return board_posting_query_service.get_posting(posting_id)


def _get_user(user_id: UserID) -> User:
    return user_service.get_user(user_id)
