"""
byceps.blueprints.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import Set

from ...services.authorization import service as authorization_service
from ...services.user import event_service as user_event_service
from ...typing import UserID

from ..authorization.registry import permission_registry


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
