"""
byceps.services.tourney.match_comment_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

from .models.match import MatchComment as DbMatchComment
from .transfer.models import MatchID, MatchCommentID


def get_comments(
    match_id: MatchID,
    *,
    party_id: Optional[PartyID] = None,
    include_hidden: bool = False,
) -> Sequence[DbMatchComment]:
    """Return comments on the match, ordered chronologically."""
    query = DbMatchComment.query \
        .for_match(match_id)

    if not include_hidden:
        query = query.filter_by(hidden=False)

    comments = query \
        .for_match(match_id) \
        .order_by(DbMatchComment.created_at) \
        .all()

    # Add creator objects.
    creator_ids = {comment.created_by_id for comment in comments}
    creators_by_id = _get_users_by_id(creator_ids, party_id=party_id)
    for comment in comments:
        comment.creator = creators_by_id[comment.created_by_id]

    # Add rendered bodies.
    for comment in comments:
        comment.body_rendered = text_markup_service.render_html(comment.body)

    return comments


def _get_users_by_id(
    user_ids: Set[UserID], *, party_id: Optional[PartyID] = None
) -> Dict[UserID, User]:
    users = user_service.find_users(
        user_ids, include_avatars=True, include_orga_flags_for_party_id=party_id
    )

    return user_service.index_users_by_id(users)


def find_comment(comment_id: MatchCommentID) -> DbMatchComment:
    """Return match comment."""
    return DbMatchComment.query.get(comment_id)


def create_comment(
    match_id: MatchID, creator_id: UserID, body: str
) -> DbMatchComment:
    """Create a comment on a match."""
    comment = DbMatchComment(match_id, creator_id, body)

    db.session.add(comment)
    db.session.commit()

    return comment


def hide_comment(comment_id: MatchCommentID, initiator_id: UserID) -> None:
    """Hide the match comment."""
    comment = DbMatchComment.query.get(comment_id)
    if comment is None:
        raise ValueError('Unknown match comment ID')

    comment.hidden = True
    comment.hidden_at = datetime.utcnow()
    comment.hidden_by_id = initiator_id

    db.session.commit()


def unhide_comment(comment_id: MatchCommentID, initiator_id: UserID) -> None:
    """Un-hide the match comment."""
    comment = DbMatchComment.query.get(comment_id)
    if comment is None:
        raise ValueError('Unknown match comment ID')

    comment.hidden = False
    comment.hidden_at = None
    comment.hidden_by_id = None

    db.session.commit()
