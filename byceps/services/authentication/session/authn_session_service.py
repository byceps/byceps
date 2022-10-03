"""
byceps.services.authentication.session.authn_session_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ....database import db, insert_ignore_on_conflict, upsert
from ....events.auth import UserLoggedIn
from ....typing import UserID

from ...site.transfer.models import SiteID
from ...user import log_service as user_log_service, service as user_service
from ...user.transfer.models import User

from .dbmodels.recent_login import DbRecentLogin
from .dbmodels.session_token import DbSessionToken
from .models.current_user import CurrentUser


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

    return db.session \
        .query(DbSessionToken) \
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
    return db.session \
        .query(DbSessionToken) \
        .filter_by(user_id=user_id) \
        .one_or_none()


def is_session_valid(user_id: UserID, auth_token: str) -> bool:
    """Return `True` if the client session is valid, `False` if not."""
    if user_id is None:
        # User ID must not be empty.
        return False

    if not auth_token:
        # Authentication token must not be empty.
        return False

    if not _is_token_valid_for_user(auth_token, user_id):
        # Session token is unknown or the user ID provided by the
        # client does not match the one stored on the server.
        return False

    return True


def _is_token_valid_for_user(token: str, user_id: UserID) -> bool:
    """Return `True` if a session token with that ID exists for that user."""
    if not user_id:
        raise ValueError('User ID is invalid.')

    subquery = db.session \
        .query(DbSessionToken) \
        .filter_by(token=token, user_id=user_id) \
        .exists()

    return db.session.query(subquery).scalar()


def log_in_user(
    user_id: UserID, ip_address: str, *, site_id: Optional[SiteID] = None
) -> tuple[str, UserLoggedIn]:
    """Create a session token and record the log in."""
    session_token = get_session_token(user_id)

    occurred_at = datetime.utcnow()
    user = user_service.get_user(user_id)

    _create_login_log_entry(user_id, occurred_at, ip_address, site_id=site_id)
    _record_recent_login(user_id, occurred_at)

    event = UserLoggedIn(
        occurred_at=occurred_at,
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        site_id=site_id,
    )

    return session_token.token, event


def _create_login_log_entry(
    user_id: UserID,
    occurred_at: datetime,
    ip_address: str,
    *,
    site_id: Optional[SiteID] = None,
) -> None:
    """Create a log entry that represents a user login."""
    data = {'ip_address': ip_address}
    if site_id:
        data['site_id'] = site_id
    user_log_service.create_entry(
        'user-logged-in', user_id, data, occurred_at=occurred_at
    )


def find_recent_login(user_id: UserID) -> Optional[datetime]:
    """Return the time of the user's most recent login, if found."""
    recent_login = db.session \
        .query(DbRecentLogin) \
        .filter_by(user_id=user_id) \
        .one_or_none()

    if recent_login is None:
        return None

    return recent_login.occurred_at


def _record_recent_login(user_id: UserID, occurred_at: datetime) -> None:
    """Store the time of the user's most recent login."""
    table = DbRecentLogin.__table__
    identifier = {'user_id': user_id}
    replacement = {'occurred_at': occurred_at}

    upsert(table, identifier, replacement)


ANONYMOUS_USER_ID = UserID(UUID('00000000-0000-0000-0000-000000000000'))


def get_anonymous_current_user(locale: Optional[str]) -> CurrentUser:
    """Return an anonymous current user object."""
    return CurrentUser(
        id=ANONYMOUS_USER_ID,
        screen_name=None,
        suspended=False,
        deleted=False,
        locale=locale,
        avatar_url=None,
        authenticated=False,
        permissions=frozenset(),
    )


def get_authenticated_current_user(
    user: User,
    locale: Optional[str],
    permissions: frozenset[str],
) -> CurrentUser:
    """Return an authenticated current user object."""
    return CurrentUser(
        id=user.id,
        screen_name=user.screen_name,
        suspended=False,  # Current user cannot be suspended.
        deleted=False,  # Current user cannot be deleted.
        locale=locale,
        avatar_url=user.avatar_url,
        authenticated=True,
        permissions=permissions,
    )
