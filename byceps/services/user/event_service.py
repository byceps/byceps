"""
byceps.services.user.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import List, Optional

from ...database import db
from ...typing import UserID

from .models.event import UserEvent, UserEventData


def create_event(
    event_type: str,
    user_id: UserID,
    data: UserEventData,
    *,
    occurred_at: Optional[datetime] = None,
) -> UserEvent:
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
) -> UserEvent:
    """Assemble, but not persist, a user event."""
    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return UserEvent(occurred_at, event_type, user_id, data)


def get_events_for_user(user_id: UserID) -> List[UserEvent]:
    """Return the events for that user."""
    return UserEvent.query \
        .filter_by(user_id=user_id) \
        .order_by(UserEvent.occurred_at) \
        .all()


def get_events_of_type_for_user(
    event_type: str, user_id: UserID
) -> List[UserEvent]:
    """Return the events of that type for that user."""
    return UserEvent.query \
        .filter_by(user_id=user_id) \
        .filter_by(event_type=event_type) \
        .order_by(UserEvent.occurred_at) \
        .all()
