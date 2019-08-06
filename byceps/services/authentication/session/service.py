"""
byceps.services.authentication.session.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ....database import db
from ....typing import UserID

from ..exceptions import AuthenticationFailed

from .models.session_token import SessionToken


def create_session_token(user_id: UserID) -> SessionToken:
    """Create a session token."""
    token = _generate_auth_token()
    created_at = datetime.utcnow()

    session_token = SessionToken(token, user_id, created_at)

    db.session.add(session_token)
    db.session.commit()

    return session_token


def _generate_auth_token() -> UUID:
    """Generate an authentication token."""
    return uuid4()


def delete_session_tokens_for_user(user_id: UserID) -> None:
    """Delete all session tokens that belong to the user."""
    db.session.query(SessionToken) \
        .filter_by(user_id=user_id) \
        .delete()
    db.session.commit()


def delete_all_session_tokens() -> int:
    """Delete all users' session tokens.

    Return the number of records deleted.
    """
    deleted_total = db.session.query(SessionToken).delete()
    db.session.commit()

    return deleted_total


def find_session_token_for_user(user_id: UserID) -> Optional[SessionToken]:
    """Return the session token for the user with that ID, or `None` if
    not found.
    """
    return SessionToken.query \
        .filter_by(user_id=user_id) \
        .one_or_none()


def authenticate_session(user_id: UserID, auth_token: str) -> None:
    """Check the client session's validity.

    Return nothing on success, or raise an exception on failure.
    """
    if user_id is None:
        # User ID must not be empty.
        raise AuthenticationFailed()

    if not auth_token:
        # Authentication token must not be empty.
        raise AuthenticationFailed()

    if not _is_token_valid_for_user(auth_token, user_id):
        # Session token is unknown or the user ID provided by the
        # client does not match the one stored on the server.
        raise AuthenticationFailed()


def _is_token_valid_for_user(token: str, user_id: UserID) -> bool:
    """Return `True` if a session token with that ID exists for that user."""
    if not user_id:
        raise ValueError('User ID is invalid.')

    session_token = SessionToken.query.get(token)

    return (session_token is not None) and (session_token.user_id == user_id)
