"""
byceps.services.user.log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from ...database import db
from ...typing import UserID

from .dbmodels.log import UserLogEntry as DbUserLogEntry, UserLogEntryData


def create_entry(
    event_type: str,
    user_id: UserID,
    data: UserLogEntryData,
    *,
    occurred_at: Optional[datetime] = None,
) -> None:
    """Create a user log entry."""
    entry = build_log_entry(event_type, user_id, data, occurred_at=occurred_at)

    db.session.add(entry)
    db.session.commit()


def build_log_entry(
    event_type: str,
    user_id: UserID,
    data: UserLogEntryData,
    *,
    occurred_at: Optional[datetime] = None,
) -> DbUserLogEntry:
    """Assemble, but not persist, a user log entry."""
    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return DbUserLogEntry(occurred_at, event_type, user_id, data)


def get_entries_for_user(user_id: UserID) -> list[DbUserLogEntry]:
    """Return the log entries for that user."""
    return db.session \
        .query(DbUserLogEntry) \
        .filter_by(user_id=user_id) \
        .order_by(DbUserLogEntry.occurred_at) \
        .all()


def get_log_entries_of_type_for_user(
    user_id: UserID, event_type: str
) -> list[DbUserLogEntry]:
    """Return the log entries of that type for that user."""
    return db.session \
        .query(DbUserLogEntry) \
        .filter_by(user_id=user_id) \
        .filter_by(event_type=event_type) \
        .order_by(DbUserLogEntry.occurred_at) \
        .all()


def delete_user_login_log_entries(occurred_before: datetime) -> int:
    """Delete login log entries which occurred before the given date.

    Return the number of deleted log entries.
    """
    num_deleted = db.session \
        .query(DbUserLogEntry) \
        .filter_by(event_type='user-logged-in') \
        .filter(DbUserLogEntry.occurred_at < occurred_before) \
        .delete()

    db.session.commit()

    return num_deleted
