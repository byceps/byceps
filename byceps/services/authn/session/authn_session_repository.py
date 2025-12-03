"""
byceps.services.authn.session.authn_session_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime
from uuid import uuid4

from sqlalchemy import delete, select

from byceps.database import db, insert_ignore_on_conflict, upsert
from byceps.services.user.log.dbmodels import DbUserLogEntry
from byceps.services.user.models.user import UserID

from .dbmodels import DbRecentLogin, DbSessionToken


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


def is_token_valid_for_user(token: str, user_id: UserID) -> bool:
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


def record_recent_login(user_id: UserID, occurred_at: datetime) -> None:
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
