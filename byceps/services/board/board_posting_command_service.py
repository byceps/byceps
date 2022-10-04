"""
byceps.services.board.board_posting_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ...database import db
from ...events.board import (
    BoardPostingCreated,
    BoardPostingHidden,
    BoardPostingUnhidden,
    BoardPostingUpdated,
)
from ...typing import UserID

from ..user import user_service
from ..user.transfer.models import User

from . import (
    board_aggregation_service,
    board_posting_query_service,
    board_topic_query_service,
)
from .dbmodels.posting import DbPosting
from .transfer.models import PostingID, TopicID


def create_posting(
    topic_id: TopicID, creator_id: UserID, body: str
) -> tuple[DbPosting, BoardPostingCreated]:
    """Create a posting in that topic."""
    topic = board_topic_query_service.get_topic(topic_id)
    creator = _get_user(creator_id)

    posting = DbPosting(topic, creator.id, body)
    db.session.add(posting)
    db.session.commit()

    board_aggregation_service.aggregate_topic(topic)

    event = BoardPostingCreated(
        occurred_at=posting.created_at,
        initiator_id=creator.id,
        initiator_screen_name=creator.screen_name,
        board_id=topic.category.board_id,
        posting_id=posting.id,
        posting_creator_id=creator.id,
        posting_creator_screen_name=creator.screen_name,
        topic_id=topic.id,
        topic_title=topic.title,
        topic_muted=topic.muted,
        url=None,
    )

    return posting, event


def update_posting(
    posting_id: PostingID, editor_id: UserID, body: str, *, commit: bool = True
) -> BoardPostingUpdated:
    """Update the posting."""
    posting = _get_posting(posting_id)
    editor = _get_user(editor_id)

    now = datetime.utcnow()

    posting.body = body.strip()
    posting.last_edited_at = now
    posting.last_edited_by_id = editor.id
    posting.edit_count += 1

    if commit:
        db.session.commit()

    posting_creator = _get_user(posting.creator_id)
    return BoardPostingUpdated(
        occurred_at=now,
        initiator_id=editor.id,
        initiator_screen_name=editor.screen_name,
        board_id=posting.topic.category.board_id,
        posting_id=posting.id,
        posting_creator_id=posting_creator.id,
        posting_creator_screen_name=posting_creator.screen_name,
        topic_id=posting.topic.id,
        topic_title=posting.topic.title,
        editor_id=editor.id,
        editor_screen_name=editor.screen_name,
        url=None,
    )


def hide_posting(
    posting_id: PostingID, moderator_id: UserID
) -> BoardPostingHidden:
    """Hide the posting."""
    posting = _get_posting(posting_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    posting.hidden = True
    posting.hidden_at = now
    posting.hidden_by_id = moderator.id
    db.session.commit()

    board_aggregation_service.aggregate_topic(posting.topic)

    posting_creator = _get_user(posting.creator_id)
    event = BoardPostingHidden(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=posting.topic.category.board_id,
        posting_id=posting.id,
        posting_creator_id=posting_creator.id,
        posting_creator_screen_name=posting_creator.screen_name,
        topic_id=posting.topic.id,
        topic_title=posting.topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )

    return event


def unhide_posting(
    posting_id: PostingID, moderator_id: UserID
) -> BoardPostingUnhidden:
    """Un-hide the posting."""
    posting = _get_posting(posting_id)
    moderator = _get_user(moderator_id)

    now = datetime.utcnow()

    # TODO: Store who un-hid the posting.
    posting.hidden = False
    posting.hidden_at = None
    posting.hidden_by_id = None
    db.session.commit()

    board_aggregation_service.aggregate_topic(posting.topic)

    posting_creator = _get_user(posting.creator_id)
    event = BoardPostingUnhidden(
        occurred_at=now,
        initiator_id=moderator.id,
        initiator_screen_name=moderator.screen_name,
        board_id=posting.topic.category.board_id,
        posting_id=posting.id,
        posting_creator_id=posting_creator.id,
        posting_creator_screen_name=posting_creator.screen_name,
        topic_id=posting.topic.id,
        topic_title=posting.topic.title,
        moderator_id=moderator.id,
        moderator_screen_name=moderator.screen_name,
        url=None,
    )

    return event


def delete_posting(posting_id: PostingID) -> None:
    """Delete a posting."""
    db.session.query(DbPosting) \
        .filter_by(id=posting_id) \
        .delete()

    db.session.commit()


def _get_posting(posting_id: PostingID) -> DbPosting:
    return board_posting_query_service.get_posting(posting_id)


def _get_user(user_id: UserID) -> User:
    return user_service.get_user(user_id)
