"""
byceps.services.tourney.match_comment_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Dict, Optional, Sequence, Set

from ...database import db
from ...services.text_markup import service as text_markup_service
from ...services.user import service as user_service
from ...services.user.transfer.models import User
from ...typing import PartyID, UserID

from .models.match_comment import MatchComment as DbMatchComment
from .transfer.models import MatchID, MatchComment, MatchCommentID


def find_comment(
    comment_id: MatchCommentID, *, party_id: Optional[PartyID] = None
) -> Optional[MatchComment]:
    """Return the comment, or `None` if not found."""
    comment = DbMatchComment.query.get(comment_id)

    if comment is None:
        return None

    # creator
    creator = _get_user(comment.created_by_id, party_id)

    # last editor
    last_editor = None
    if comment.last_edited_by_id:
        last_editor = _get_user(comment.last_edited_by_id, party_id)

    # moderator
    moderator = None
    if comment.hidden_by_id:
        moderator = _get_user(comment.hidden_by_id, party_id)

    return _db_entity_to_comment(
        comment, creator, last_editor=last_editor, moderator=moderator,
    )


def get_comment(
    comment_id: MatchCommentID, *, party_id: Optional[PartyID] = None
) -> MatchComment:
    """Return the comment.

    Raise exception if comment ID is unknown.
    """
    comment = find_comment(comment_id)

    if comment is None:
        raise ValueError('Unknown match comment ID')

    return comment


def get_comments(
    match_id: MatchID,
    *,
    party_id: Optional[PartyID] = None,
    include_hidden: bool = False,
) -> Sequence[MatchComment]:
    """Return comments on the match, ordered chronologically."""
    query = DbMatchComment.query \
        .for_match(match_id)

    if not include_hidden:
        query = query.filter_by(hidden=False)

    db_comments = query \
        .for_match(match_id) \
        .order_by(DbMatchComment.created_at) \
        .all()

    # creators
    creator_ids = {comment.created_by_id for comment in db_comments}
    creators_by_id = _get_users_by_id(creator_ids, party_id=party_id)

    # last editors
    last_editor_ids = {
        comment.last_edited_by_id
        for comment in db_comments
        if comment.last_edited_by_id
    }
    last_editors_by_id = _get_users_by_id(last_editor_ids, party_id=party_id)

    # moderators
    moderator_ids = {
        comment.hidden_by_id for comment in db_comments if comment.hidden_by_id
    }
    moderators_by_id = _get_users_by_id(moderator_ids, party_id=party_id)

    comments = []
    for db_comment in db_comments:
        creator = creators_by_id[db_comment.created_by_id]
        last_editor = last_editors_by_id.get(db_comment.last_edited_by_id)
        moderator = moderators_by_id.get(db_comment.hidden_by_id)

        comment = _db_entity_to_comment(
            db_comment, creator, last_editor=last_editor, moderator=moderator,
        )
        comments.append(comment)

    return comments


def _get_users_by_id(
    user_ids: Set[UserID], *, party_id: Optional[PartyID] = None
) -> Dict[UserID, User]:
    users = user_service.find_users(
        user_ids, include_avatars=True, include_orga_flags_for_party_id=party_id
    )

    return user_service.index_users_by_id(users)


def create_comment(
    match_id: MatchID, creator_id: UserID, body: str
) -> MatchComment:
    """Create a comment on a match."""
    comment = DbMatchComment(match_id, creator_id, body)

    db.session.add(comment)
    db.session.commit()

    return get_comment(comment.id)


def update_comment(
    comment_id: MatchCommentID, editor_id: UserID, body: str
) -> MatchComment:
    """Update a comment on a match."""
    comment = _get_db_comment(comment_id)

    comment.body = body
    comment.last_edited_at = datetime.utcnow()
    comment.last_edited_by_id = editor_id

    db.session.commit()

    return get_comment(comment.id)


def hide_comment(comment_id: MatchCommentID, initiator_id: UserID) -> None:
    """Hide the match comment."""
    comment = _get_db_comment(comment_id)

    comment.hidden = True
    comment.hidden_at = datetime.utcnow()
    comment.hidden_by_id = initiator_id

    db.session.commit()


def unhide_comment(comment_id: MatchCommentID, initiator_id: UserID) -> None:
    """Un-hide the match comment."""
    comment = _get_db_comment(comment_id)

    comment.hidden = False
    comment.hidden_at = None
    comment.hidden_by_id = None

    db.session.commit()


def _get_db_comment(comment_id: MatchCommentID) -> DbMatchComment:
    """Return the comment as database entity.

    Raise exception if comment ID is unknown.
    """
    comment = DbMatchComment.query.get(comment_id)

    if comment is None:
        raise ValueError('Unknown match comment ID')

    return comment


def _get_user(user_id: UserID, party_id: Optional[PartyID] = None) -> User:
    return user_service.get_user(
        user_id, include_avatar=True, include_orga_flag_for_party_id=party_id
    )


def _db_entity_to_comment(
    comment: DbMatchComment,
    creator: User,
    *,
    last_editor: Optional[User],
    moderator: Optional[User],
) -> MatchComment:
    body_html = text_markup_service.render_html(comment.body)

    return MatchComment(
        comment.id,
        comment.match_id,
        comment.created_at,
        creator,
        comment.body,
        body_html,
        comment.last_edited_at,
        last_editor,
        comment.hidden,
        comment.hidden_at,
        moderator,
    )
