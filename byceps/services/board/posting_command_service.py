"""
byceps.services.board.posting_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Tuple

from ...database import db
from ...events.board import (
    BoardPostingCreated,
    BoardPostingHidden,
    BoardPostingUnhidden,
)
from ...typing import UserID

from .aggregation_service import aggregate_topic
from .models.posting import Posting as DbPosting
from .models.topic import Topic as DbTopic


def create_posting(
    topic: DbTopic, creator_id: UserID, body: str
) -> Tuple[DbPosting, BoardPostingCreated]:
    """Create a posting in that topic."""
    posting = DbPosting(topic, creator_id, body)
    db.session.add(posting)
    db.session.commit()

    aggregate_topic(topic)

    event = BoardPostingCreated(posting_id=posting.id, url=None)

    return posting, event


def update_posting(
    posting: DbPosting, editor_id: UserID, body: str, *, commit: bool = True
) -> None:
    """Update the posting."""
    posting.body = body.strip()
    posting.last_edited_at = datetime.utcnow()
    posting.last_edited_by_id = editor_id
    posting.edit_count += 1

    if commit:
        db.session.commit()


def hide_posting(
    posting: DbPosting, moderator_id: UserID
) -> BoardPostingHidden:
    """Hide the posting."""
    posting.hidden = True
    posting.hidden_at = datetime.utcnow()
    posting.hidden_by_id = moderator_id
    db.session.commit()

    aggregate_topic(posting.topic)

    event = BoardPostingHidden(
        posting_id=posting.id, moderator_id=moderator_id, url=None
    )

    return event


def unhide_posting(
    posting: DbPosting, moderator_id: UserID
) -> BoardPostingUnhidden:
    """Un-hide the posting."""
    # TODO: Store who un-hid the posting.
    posting.hidden = False
    posting.hidden_at = None
    posting.hidden_by_id = None
    db.session.commit()

    aggregate_topic(posting.topic)

    event = BoardPostingUnhidden(
        posting_id=posting.id, moderator_id=moderator_id, url=None
    )

    return event
