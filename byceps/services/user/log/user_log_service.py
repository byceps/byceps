"""
byceps.services.user.log.user_log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.user import user_service
from byceps.services.user.models.user import UserID

from .dbmodels import DbUserLogEntry
from .models import UserLogEntry


def persist_entry(entry: UserLogEntry) -> None:
    """Store a user log entry."""
    db_entry = to_db_entry(entry)
    db.session.add(db_entry)
    db.session.commit()


def to_db_entry(entry: UserLogEntry) -> DbUserLogEntry:
    """Convert log entry to database entity."""
    return DbUserLogEntry(
        entry.id,
        entry.occurred_at,
        entry.event_type,
        entry.user.id,
        entry.initiator.id if entry.initiator else None,
        entry.data,
    )


def get_entries_for_user(user_id: UserID) -> list[UserLogEntry]:
    """Return the log entries for that user."""
    db_entries = db.session.scalars(
        select(DbUserLogEntry)
        .options(
            db.joinedload(DbUserLogEntry.user),
            db.joinedload(DbUserLogEntry.initiator),
        )
        .filter_by(user_id=user_id)
        .order_by(DbUserLogEntry.occurred_at)
    ).all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def get_entries_of_type_for_user(
    user_id: UserID, event_type: str
) -> list[UserLogEntry]:
    """Return the log entries of that type for that user."""
    db_entries = db.session.scalars(
        select(DbUserLogEntry)
        .options(
            db.joinedload(DbUserLogEntry.user),
            db.joinedload(DbUserLogEntry.initiator),
        )
        .filter_by(user_id=user_id)
        .filter_by(event_type=event_type)
        .order_by(DbUserLogEntry.occurred_at)
    ).all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def _db_entity_to_entry(db_entry: DbUserLogEntry) -> UserLogEntry:
    return UserLogEntry(
        id=db_entry.id,
        occurred_at=db_entry.occurred_at,
        event_type=db_entry.event_type,
        user=user_service._db_entity_to_user(db_entry.user),
        initiator=user_service._db_entity_to_user(db_entry.initiator)
        if db_entry.initiator
        else None,
        data=db_entry.data.copy(),
    )
