"""
byceps.services.authz.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.authz.models import RoleID
from byceps.services.core.events import _BaseEvent, EventUser


@dataclass(frozen=True)
class _AuthzUserRoleEvent(_BaseEvent):
    user: EventUser
    role_id: RoleID


@dataclass(frozen=True)
class RoleAssignedToUserEvent(_AuthzUserRoleEvent):
    pass


@dataclass(frozen=True)
class RoleDeassignedFromUserEvent(_AuthzUserRoleEvent):
    pass
