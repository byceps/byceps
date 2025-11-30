"""
byceps.services.user.log.user_log_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models import UserLogEntry, UserLogEntryData


def build_entry(
    event_type: str,
    user: User,
    data: UserLogEntryData,
    *,
    occurred_at: datetime | None = None,
    initiator: User | None = None,
) -> UserLogEntry:
    """Assemble a user log entry."""
    entry_id = generate_uuid7()

    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return UserLogEntry(
        id=entry_id,
        occurred_at=occurred_at,
        event_type=event_type,
        user=user,
        initiator_id=initiator.id if initiator else None,
        data=data,
    )
