"""
byceps.services.user.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from ...database import db
from ...typing import UserID

from .dbmodels.event import UserEvent as DbUserEvent, UserEventData


def create_event(
    event_type: str,
    user_id: UserID,
    data: UserEventData,
    *,
    occurred_at: Optional[datetime] = None,
) -> DbUserEvent:
    """Create a user event."""
    event = build_event(event_type, user_id, data, occurred_at=occurred_at)

    db.session.add(event)
    db.session.commit()

    return event


def build_event(
    event_type: str,
    user_id: UserID,
    data: UserEventData,
    *,
    occurred_at: Optional[datetime] = None,
) -> DbUserEvent:
    """Assemble, but not persist, a user event."""
    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return DbUserEvent(occurred_at, event_type, user_id, data)


def get_events_for_user(user_id: UserID) -> list[DbUserEvent]:
    """Return the events for that user."""
    return DbUserEvent.query \
        .filter_by(user_id=user_id) \
        .order_by(DbUserEvent.occurred_at) \
        .all()


def get_events_of_type_for_user(
    user_id: UserID, event_type: str
) -> list[DbUserEvent]:
    """Return the events of that type for that user."""
    return DbUserEvent.query \
        .filter_by(user_id=user_id) \
        .filter_by(event_type=event_type) \
        .order_by(DbUserEvent.occurred_at) \
        .all()


def delete_user_login_events(occurred_before: datetime) -> int:
    """Delete login events which occurred before the given date.

    Return the number of deleted events.
    """
    num_deleted = DbUserEvent.query \
        .filter_by(event_type='user-logged-in') \
        .filter(DbUserEvent.occurred_at < occurred_before) \
        .delete()

    db.session.commit()

    return num_deleted
