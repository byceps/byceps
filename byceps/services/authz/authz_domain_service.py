"""
byceps.services.authz.authz_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.events.authz import (
    RoleAssignedToUserEvent,
    RoleDeassignedFromUserEvent,
)
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models import RoleID


def assign_role_to_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> tuple[RoleAssignedToUserEvent, UserLogEntry]:
    """Assign the role to the user."""
    occurred_at = datetime.utcnow()

    event = _build_role_assigned_to_user_event(
        occurred_at, user, role_id, initiator
    )
    log_entry = _build_role_assigned_log_entry(
        occurred_at, user, role_id, initiator
    )

    return event, log_entry


def _build_role_assigned_to_user_event(
    occurred_at: datetime, user: User, role_id: RoleID, initiator: User | None
) -> RoleAssignedToUserEvent:
    return RoleAssignedToUserEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        role_id=role_id,
    )


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
        initiator_id=initiator.id if initiator else None,
        data=data,
    )


def deassign_role_from_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> tuple[RoleDeassignedFromUserEvent, UserLogEntry]:
    """Deassign the role from the user."""
    occurred_at = datetime.utcnow()

    event = _build_role_deassigned_from_user_event(
        occurred_at, user, role_id, initiator
    )
    log_entry = _build_role_deassigned_log_entry(
        occurred_at, user, role_id, initiator
    )

    return event, log_entry


def _build_role_deassigned_from_user_event(
    occurred_at: datetime, user: User, role_id: RoleID, initiator: User | None
) -> RoleDeassignedFromUserEvent:
    return RoleDeassignedFromUserEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        role_id=role_id,
    )


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
        initiator_id=initiator.id if initiator else None,
        data=data,
    )
