"""
byceps.services.authentication.session.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from ....database import db, insert_ignore_on_conflict, upsert
from ....typing import UserID

from ...user import event_service as user_event_service

from ..exceptions import AuthenticationFailed

from .models.recent_login import RecentLogin as DbRecentLogin
from .models.session_token import SessionToken as DbSessionToken


def get_session_token(user_id: UserID) -> DbSessionToken:
    """Return session token.

    Create one if none exists for the user.
    """
    table = DbSessionToken.__table__

    values = {
        'user_id': user_id,
        'token': uuid4(),
        'created_at': datetime.utcnow(),
    }

    insert_ignore_on_conflict(table, values)

    return DbSessionToken.query \
        .filter_by(user_id=user_id) \
        .one()


def delete_session_tokens_for_user(user_id: UserID) -> None:
    """Delete all session tokens that belong to the user."""
    db.session.query(DbSessionToken) \
        .filter_by(user_id=user_id) \
        .delete()
    db.session.commit()


def delete_all_session_tokens() -> int:
    """Delete all users' session tokens.

    Return the number of records deleted.
    """
    deleted_total = db.session.query(DbSessionToken).delete()
    db.session.commit()

    return deleted_total


def find_session_token_for_user(user_id: UserID) -> Optional[DbSessionToken]:
    """Return the session token for the user with that ID, or `None` if
    not found.
    """
    return DbSessionToken.query \
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

    subquery = DbSessionToken.query \
        .filter_by(token=token, user_id=user_id) \
        .exists()

    return db.session.query(subquery).scalar()


def create_login_event(user_id: UserID, ip_address: str) -> None:
    """Create an event that represents a user login."""
    data = {'ip_address': ip_address}
    user_event_service.create_event('user-logged-in', user_id, data)


def find_recent_login(user_id: UserID) -> Optional[datetime]:
    """Return the time of the user's most recent login, if found."""
    recent_login = DbRecentLogin.query \
        .filter_by(user_id=user_id) \
        .one_or_none()

    if recent_login is None:
        return None

    return recent_login.occurred_at


def record_recent_login(user_id: UserID) -> datetime:
    """Store the time of the user's most recent login."""
    occurred_at = datetime.utcnow()

    table = DbRecentLogin.__table__
    identifier = {'user_id': user_id}
    replacement = {'occurred_at': occurred_at}

    upsert(table, identifier, replacement)

    return occurred_at
