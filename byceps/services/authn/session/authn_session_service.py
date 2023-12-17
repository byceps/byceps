"""
byceps.services.authn.session.authn_session_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, select

from byceps.database import db, insert_ignore_on_conflict, upsert
from byceps.events.authn import UserLoggedInEvent
from byceps.events.base import EventSite, EventUser
from byceps.services.site.models import Site, SiteID
from byceps.services.user import user_log_service
from byceps.services.user.dbmodels.log import DbUserLogEntry
from byceps.services.user.models.user import User, UserID

from .dbmodels import DbRecentLogin, DbSessionToken
from .models import CurrentUser


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

    return db.session.execute(
        select(DbSessionToken).filter_by(user_id=user_id)
    ).scalar_one()


def delete_session_tokens_for_user(user_id: UserID) -> None:
    """Delete all session tokens that belong to the user."""
    db.session.execute(
        delete(DbSessionToken).where(DbSessionToken.user_id == user_id)
    )
    db.session.commit()


def delete_all_session_tokens() -> int:
    """Delete all users' session tokens.

    Return the number of records deleted.
    """
    result = db.session.execute(delete(DbSessionToken))
    db.session.commit()

    num_deleted = result.rowcount
    return num_deleted


def find_session_token_for_user(user_id: UserID) -> DbSessionToken | None:
    """Return the session token for the user with that ID, or `None` if
    not found.
    """
    return db.session.execute(
        select(DbSessionToken).filter_by(user_id=user_id)
    ).scalar_one_or_none()


def is_session_valid(user_id: UserID, auth_token: str) -> bool:
    """Return `True` if the client session is valid, `False` if not."""
    if not user_id:
        # User ID must not be empty.
        return False

    if not auth_token:
        # Authentication token must not be empty.
        return False

    return _is_token_valid_for_user(auth_token, user_id)


def _is_token_valid_for_user(token: str, user_id: UserID) -> bool:
    """Return `True` if a session token with that ID exists for that user.

    Return `False` if the session token is unknown or the user ID
    provided by the client does not match the one stored on the server.
    """
    return (
        db.session.scalar(
            select(
                db.exists()
                .where(DbSessionToken.token == token)
                .where(DbSessionToken.user_id == user_id)
            )
        )
        or False
    )


def log_in_user(
    user: User,
    *,
    ip_address: str | None = None,
    site: Site | None = None,
) -> tuple[str, UserLoggedInEvent]:
    """Create a session token and record the log in."""
    session_token = get_session_token(user.id)

    occurred_at = datetime.utcnow()

    _create_login_log_entry(
        user.id,
        occurred_at,
        ip_address=ip_address,
        site_id=site.id if site else None,
    )
    _record_recent_login(user.id, occurred_at)

    event = UserLoggedInEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(user),
        site=EventSite.from_site(site) if site else None,
    )

    return session_token.token, event


def _create_login_log_entry(
    user_id: UserID,
    occurred_at: datetime,
    *,
    ip_address: str | None = None,
    site_id: SiteID | None = None,
) -> None:
    """Create a log entry that represents a user login."""
    data = {}

    if ip_address:
        data['ip_address'] = ip_address

    if site_id:
        data['site_id'] = site_id

    user_log_service.create_entry(
        'user-logged-in', user_id, data, occurred_at=occurred_at
    )


def _record_recent_login(user_id: UserID, occurred_at: datetime) -> None:
    """Store the time of the user's most recent login."""
    table = DbRecentLogin.__table__
    identifier = {'user_id': user_id}
    replacement = {'occurred_at': occurred_at}

    upsert(table, identifier, replacement)


def find_recent_login(user_id: UserID) -> datetime | None:
    """Return the time of the user's most recent login, if found."""
    db_recent_login = db.session.execute(
        select(DbRecentLogin).filter_by(user_id=user_id)
    ).scalar_one_or_none()

    if db_recent_login is None:
        return None

    return db_recent_login.occurred_at


def find_recent_logins_for_users(
    user_ids: set[UserID],
) -> dict[UserID, datetime]:
    """Return the time of the users' most recent logins, if found."""
    db_recent_logins = db.session.scalars(
        select(DbRecentLogin).filter(DbRecentLogin.user_id.in_(user_ids))
    ).all()

    return {
        db_recent_login.user_id: db_recent_login.occurred_at
        for db_recent_login in db_recent_logins
    }


def find_logins_for_ip_address(
    ip_address: str,
) -> Sequence[tuple[datetime, UserID]]:
    """Return login timestamp and user ID for logins from the given IP
    address.
    """
    return (
        db.session.execute(
            select(
                DbUserLogEntry.occurred_at,
                DbUserLogEntry.user_id,
            )
            .filter_by(event_type='user-logged-in')
            .filter(DbUserLogEntry.data['ip_address'].astext == ip_address)
            .order_by(DbUserLogEntry.occurred_at)
        )
        .tuples()
        .all()
    )


def delete_login_entries(occurred_before: datetime) -> int:
    """Delete login log entries which occurred before the given date.

    Return the number of deleted log entries.
    """
    result = db.session.execute(
        delete(DbUserLogEntry)
        .filter_by(event_type='user-logged-in')
        .filter(DbUserLogEntry.occurred_at < occurred_before)
    )
    db.session.commit()

    num_deleted = result.rowcount
    return num_deleted


ANONYMOUS_USER_ID = UserID(UUID('00000000-0000-0000-0000-000000000000'))


def get_anonymous_current_user(locale: str | None) -> CurrentUser:
    """Return an anonymous current user object."""
    return CurrentUser(
        id=ANONYMOUS_USER_ID,
        screen_name=None,
        initialized=True,
        suspended=False,
        deleted=False,
        locale=locale,
        avatar_url=None,
        authenticated=False,
        permissions=frozenset(),
    )


def get_authenticated_current_user(
    user: User,
    locale: str | None,
    permissions: frozenset[str],
) -> CurrentUser:
    """Return an authenticated current user object."""
    return CurrentUser(
        id=user.id,
        screen_name=user.screen_name,
        initialized=True,  # Current user has to be initialized.
        suspended=False,  # Current user cannot be suspended.
        deleted=False,  # Current user cannot be deleted.
        locale=locale,
        avatar_url=user.avatar_url,
        authenticated=True,
        permissions=permissions,
    )
