"""
byceps.blueprints.common.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum
from typing import Optional, Set

from ....services.authentication.session.models.current_user import CurrentUser
from ....services.authorization import service as authorization_service
from ....typing import PartyID, UserID
from ....util.framework.permission_registry import permission_registry
from ....util import user_session

from ...admin.core.authorization import AdminPermission


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
