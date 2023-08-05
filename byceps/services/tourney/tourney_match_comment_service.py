"""
byceps.services.tourney.tourney_match_comment_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.services.text_markup import text_markup_service
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import UserID

from .dbmodels.match_comment import DbMatchComment
from .models import MatchComment, MatchCommentID, MatchID


def find_comment(comment_id: MatchCommentID) -> MatchComment | None:
    """Return the comment, or `None` if not found."""
    db_comment = db.session.get(DbMatchComment, comment_id)

    if db_comment is None:
        return None

    # creator
    creator = _get_user(db_comment.created_by_id)

    # last editor
    last_editor = None
    if db_comment.last_edited_by_id:
        last_editor = _get_user(db_comment.last_edited_by_id)

    # moderator
    moderator = None
    if db_comment.hidden_by_id:
        moderator = _get_user(db_comment.hidden_by_id)

    return _db_entity_to_comment(
        db_comment,
        creator,
        last_editor=last_editor,
        moderator=moderator,
    )


def get_comment(comment_id: MatchCommentID) -> MatchComment:
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
    include_hidden: bool = False,
) -> list[MatchComment]:
    """Return comments on the match, ordered chronologically."""
    stmt = select(DbMatchComment).filter_by(match_id=match_id)

    if not include_hidden:
        stmt = stmt.filter_by(hidden=False)

    db_comments = db.session.scalars(
        stmt.order_by(DbMatchComment.created_at)
    ).all()

    # creators
    creator_ids = {comment.created_by_id for comment in db_comments}
    creators_by_id = _get_users_by_id(creator_ids)

    # last editors
    last_editor_ids = {
        comment.last_edited_by_id
        for comment in db_comments
        if comment.last_edited_by_id
    }
    last_editors_by_id = _get_users_by_id(last_editor_ids)

    # moderators
    moderator_ids = {
        comment.hidden_by_id for comment in db_comments if comment.hidden_by_id
    }
    moderators_by_id = _get_users_by_id(moderator_ids)

    comments = []
    for db_comment in db_comments:
        creator = creators_by_id[db_comment.created_by_id]
        last_editor = last_editors_by_id.get(db_comment.last_edited_by_id)
        moderator = moderators_by_id.get(db_comment.hidden_by_id)

        comment = _db_entity_to_comment(
            db_comment,
            creator,
            last_editor=last_editor,
            moderator=moderator,
        )
        comments.append(comment)

    return comments


def _get_users_by_id(user_ids: set[UserID]) -> dict[UserID, User]:
    users = user_service.get_users(user_ids, include_avatars=True)
    return user_service.index_users_by_id(users)


def create_comment(match_id: MatchID, creator: User, body: str) -> MatchComment:
    """Create a comment on a match."""
    db_comment = DbMatchComment(match_id, creator.id, body)

    db.session.add(db_comment)
    db.session.commit()

    return get_comment(db_comment.id)


def update_comment(
    comment_id: MatchCommentID, editor: User, body: str
) -> MatchComment:
    """Update a comment on a match."""
    db_comment = _get_db_comment(comment_id)

    db_comment.body = body
    db_comment.last_edited_at = datetime.utcnow()
    db_comment.last_edited_by_id = editor.id

    db.session.commit()

    return get_comment(db_comment.id)


def hide_comment(comment_id: MatchCommentID, initiator: User) -> None:
    """Hide the match comment."""
    db_comment = _get_db_comment(comment_id)

    db_comment.hidden = True
    db_comment.hidden_at = datetime.utcnow()
    db_comment.hidden_by_id = initiator.id

    db.session.commit()


def unhide_comment(comment_id: MatchCommentID, initiator: User) -> None:
    """Un-hide the match comment."""
    db_comment = _get_db_comment(comment_id)

    db_comment.hidden = False
    db_comment.hidden_at = None
    db_comment.hidden_by_id = None

    db.session.commit()


def _get_db_comment(comment_id: MatchCommentID) -> DbMatchComment:
    """Return the comment as database entity.

    Raise exception if comment ID is unknown.
    """
    db_comment = db.session.get(DbMatchComment, comment_id)

    if db_comment is None:
        raise ValueError('Unknown match comment ID')

    return db_comment


def _get_user(user_id: UserID) -> User:
    return user_service.get_user(user_id, include_avatar=True)


def _db_entity_to_comment(
    db_comment: DbMatchComment,
    creator: User,
    *,
    last_editor: User | None,
    moderator: User | None,
) -> MatchComment:
    body_html = text_markup_service.render_html(db_comment.body)

    return MatchComment(
        id=db_comment.id,
        match_id=db_comment.match_id,
        created_at=db_comment.created_at,
        created_by=creator,
        body_text=db_comment.body,
        body_html=body_html,
        last_edited_at=db_comment.last_edited_at,
        last_edited_by=last_editor,
        hidden=db_comment.hidden,
        hidden_at=db_comment.hidden_at,
        hidden_by=moderator,
    )
