"""
byceps.services.authorization.authz_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models import RoleID


def assign_role_to_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> UserLogEntry:
    """Assign the role to the user."""
    occurred_at = datetime.utcnow()

    log_entry = _build_role_assigned_log_entry(
        occurred_at, user, role_id, initiator
    )

    return log_entry


def _build_role_assigned_log_entry(
    occurred_at: datetime, user: User, role_id: RoleID, initiator: User | None
) -> UserLogEntry:
    data = {'role_id': str(role_id)}
    if initiator:
        data['initiator_id'] = str(initiator.id)

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='role-assigned',
        user_id=user.id,
        data=data,
    )


def deassign_role_from_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> UserLogEntry:
    """Deassign the role from the user."""
    occurred_at = datetime.utcnow()

    log_entry = _build_role_deassigned_log_entry(
        occurred_at, user, role_id, initiator
    )

    return log_entry


def _build_role_deassigned_log_entry(
    occurred_at: datetime, user: User, role_id: RoleID, initiator: User | None
) -> UserLogEntry:
    data = {'role_id': str(role_id)}
    if initiator:
        data['initiator_id'] = str(initiator.id)

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='role-deassigned',
        user_id=user.id,
        data=data,
    )
