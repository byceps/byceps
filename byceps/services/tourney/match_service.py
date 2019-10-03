"""
byceps.services.tourney.match_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Optional, Sequence, Set

from ...database import db
from ...services.text_markup import service as text_markup_service
from ...services.user import service as user_service
from ...services.user.transfer.models import User
from ...typing import PartyID, UserID

from .models.match import Match, MatchID, MatchComment, MatchCommentID


# -------------------------------------------------------------------- #
# matches


def create_match() -> MatchID:
    """Create a match."""
    match = Match()

    db.session.add(match)
    db.session.commit()

    return match.id


def find_match(match_id: MatchID) -> Optional[Match]:
    """Return the match with that id, or `None` if not found."""
    return Match.query.get(match_id)


# -------------------------------------------------------------------- #
# comments


def get_comments(
    match_id: MatchID, party_id: PartyID
) -> Sequence[MatchComment]:
    """Return comments on the match, ordered chronologically."""
    comments = MatchComment.query \
        .for_match(match_id) \
        .order_by(MatchComment.created_at) \
        .all()

    # Add creator objects.
    creator_ids = {comment.created_by_id for comment in comments}
    creators_by_id = _get_users_by_id(creator_ids, party_id)
    for comment in comments:
        comment.creator = creators_by_id[comment.created_by_id]

    # Add rendered bodies.
    for comment in comments:
        comment.body_rendered = text_markup_service.render_html(comment.body)

    return comments


def _get_users_by_id(
    user_ids: Set[UserID], party_id: PartyID
) -> Dict[UserID, User]:
    users = user_service.find_users(
        user_ids, include_avatars=True, include_orga_flags_for_party_id=party_id
    )

    return user_service.index_users_by_id(users)


def create_comment(
    match_id: MatchID, creator_id: UserID, body: str
) -> MatchComment:
    """Create a comment on a match."""
    comment = MatchComment(match_id, creator_id, body)

    db.session.add(comment)
    db.session.commit()

    return comment


def hide_comment(comment_id: MatchCommentID, initiator_id: UserID) -> None:
    """Hide the match comment."""
    comment = MatchComment.query.get(comment_id)
    if comment is None:
        raise ValueError('Unknown match comment ID')

    comment.hidden = True
    comment.hidden_at = datetime.utcnow()
    comment.hidden_by_id = initiator_id

    db.session.commit()


def unhide_comment(comment_id: MatchCommentID, initiator_id: UserID) -> None:
    """Un-hide the match comment."""
    comment = MatchComment.query.get(comment_id)
    if comment is None:
        raise ValueError('Unknown match comment ID')

    comment.hidden = False
    comment.hidden_at = None
    comment.hidden_by_id = None

    db.session.commit()
