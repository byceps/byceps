"""
byceps.blueprints.common.authentication.login.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from .....services.authentication.session.models.current_user import CurrentUser
from .....typing import PartyID
from .....util.authorization import get_permissions_for_user
from .....util import user_session

from ....admin.core.authorization import AdminPermission


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
