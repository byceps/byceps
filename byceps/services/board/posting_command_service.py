"""
byceps.services.board.posting_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Tuple

from ...database import db
from ...events.board import (
    BoardPostingCreated,
    BoardPostingHidden,
    BoardPostingUnhidden,
    BoardPostingUpdated,
)
from ...typing import UserID

from .aggregation_service import aggregate_topic
from .models.posting import Posting as DbPosting
from . import posting_query_service
from . import topic_query_service
from .transfer.models import PostingID, TopicID


def create_posting(
    topic_id: TopicID, creator_id: UserID, body: str
) -> Tuple[DbPosting, BoardPostingCreated]:
    """Create a posting in that topic."""
    topic = topic_query_service.get_topic(topic_id)

    posting = DbPosting(topic, creator_id, body)
    db.session.add(posting)
    db.session.commit()

    aggregate_topic(topic)

    event = BoardPostingCreated(
        occurred_at=posting.created_at, posting_id=posting.id, url=None
    )

    return posting, event


def update_posting(
    posting_id: PostingID, editor_id: UserID, body: str, *, commit: bool = True
) -> BoardPostingUpdated:
    """Update the posting."""
    posting = _get_posting(posting_id)

    now = datetime.utcnow()

    posting.body = body.strip()
    posting.last_edited_at = now
    posting.last_edited_by_id = editor_id
    posting.edit_count += 1

    if commit:
        db.session.commit()

    return BoardPostingUpdated(
        occurred_at=now, posting_id=posting.id, editor_id=editor_id, url=None
    )


def hide_posting(
    posting_id: PostingID, moderator_id: UserID
) -> BoardPostingHidden:
    """Hide the posting."""
    posting = _get_posting(posting_id)

    now = datetime.utcnow()

    posting.hidden = True
    posting.hidden_at = now
    posting.hidden_by_id = moderator_id
    db.session.commit()

    aggregate_topic(posting.topic)

    event = BoardPostingHidden(
        occurred_at=now,
        posting_id=posting.id,
        moderator_id=moderator_id,
        url=None,
    )

    return event


def unhide_posting(
    posting_id: PostingID, moderator_id: UserID
) -> BoardPostingUnhidden:
    """Un-hide the posting."""
    posting = _get_posting(posting_id)

    now = datetime.utcnow()

    # TODO: Store who un-hid the posting.
    posting.hidden = False
    posting.hidden_at = None
    posting.hidden_by_id = None
    db.session.commit()

    aggregate_topic(posting.topic)

    event = BoardPostingUnhidden(
        occurred_at=now,
        posting_id=posting.id,
        moderator_id=moderator_id,
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
    return posting_query_service.get_posting(posting_id)
