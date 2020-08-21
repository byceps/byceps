"""
byceps.blueprints.common.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import Optional, Set

from ....services.authentication.session.models.current_user import CurrentUser
from ....services.authorization import service as authorization_service
from ....services.user import event_service as user_event_service
from ....typing import PartyID, UserID

from ...admin.core.authorization import AdminPermission

from ..authorization.registry import permission_registry

from . import session as user_session


def create_login_event(user_id: UserID, ip_address: str) -> None:
    """Create an event representing a user login."""
    data = {
        'ip_address': ip_address,
    }

    user_event_service.create_event('user-logged-in', user_id, data)


def get_permissions_for_user(user_id: UserID) -> Set[Enum]:
    """Return the permissions this user has been granted."""
    permission_ids = authorization_service.get_permission_ids_for_user(user_id)
    return permission_registry.get_enum_members(permission_ids)


def get_current_user(
    is_admin_mode: bool, *, party_id: Optional[PartyID] = None
) -> CurrentUser:
    user = user_session.get_user(party_id=party_id)

    if user is None:
        return CurrentUser.create_anonymous()

    permissions = get_permissions_for_user(user.id)

    if is_admin_mode and (AdminPermission.access not in permissions):
        # The user lacks the admin access permission which is
        # required to enter the admin area.
        return CurrentUser.create_anonymous()

    return CurrentUser.create_from_user(user, permissions)
