"""
byceps.services.authz.authz_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.log import user_log_domain_service
from byceps.services.user.log.models import UserLogEntry
from byceps.services.user.models.user import User

from .events import RoleAssignedToUserEvent, RoleDeassignedFromUserEvent
from .models import RoleID


def assign_role_to_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> tuple[RoleAssignedToUserEvent, UserLogEntry]:
    """Assign the role to the user."""
    occurred_at = datetime.utcnow()

    event = _build_role_assigned_to_user_event(
        occurred_at, user, role_id, initiator
    )

    log_entry = _build_role_assigned_log_entry(event)

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
    event: RoleAssignedToUserEvent,
) -> UserLogEntry:
    data = {'role_id': str(event.role_id)}

    return user_log_domain_service.build_entry(
        'role-assigned',
        event.user,
        data,
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )


def deassign_role_from_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> tuple[RoleDeassignedFromUserEvent, UserLogEntry]:
    """Deassign the role from the user."""
    occurred_at = datetime.utcnow()

    event = _build_role_deassigned_from_user_event(
        occurred_at, user, role_id, initiator
    )

    log_entry = _build_role_deassigned_log_entry(event)

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
    event: RoleDeassignedFromUserEvent,
) -> UserLogEntry:
    data = {'role_id': str(event.role_id)}

    return user_log_domain_service.build_entry(
        'role-deassigned',
        event.user,
        data,
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )
