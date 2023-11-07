"""
byceps.services.board.board_posting_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.models.user import User, UserID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .errors import (
    ReactionDeniedError,
    ReactionDoesNotExistError,
    ReactionExistsError,
)
from .models import PostingID, PostingReaction


def add_reaction(
    posting_id: PostingID,
    posting_creator_id: UserID,
    user: User,
    kind: str,
    reaction_exists: bool,
) -> Result[PostingReaction, ReactionDeniedError | ReactionExistsError]:
    """Add user reaction to the posting."""
    if user.id == posting_creator_id:
        return Err(ReactionDeniedError())

    if reaction_exists:
        return Err(ReactionExistsError())

    reaction_id = generate_uuid7()
    created_at = datetime.utcnow()

    reaction = PostingReaction(
        id=reaction_id,
        created_at=created_at,
        posting_id=posting_id,
        user_id=user.id,
        kind=kind,
    )

    return Ok(reaction)


def remove_reaction(
    posting_id: PostingID,
    posting_creator_id: UserID,
    user: User,
    kind: str,
    reaction_exists: bool,
) -> Result[None, ReactionDeniedError | ReactionDoesNotExistError]:
    """Remove user reaction from the posting."""
    if user.id == posting_creator_id:
        return Err(ReactionDeniedError())

    if not reaction_exists:
        return Err(ReactionDoesNotExistError())

    return Ok(None)
