"""
byceps.blueprints.common.authentication.login.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum
from typing import Optional, Set

from .....services.authentication.session.models.current_user import CurrentUser
from .....typing import PartyID
from .....util.authorization import get_permissions_for_user
from .....util import user_session


def get_current_user(
    required_permissions: Set[Enum],
    *,
    party_id: Optional[PartyID] = None,
) -> CurrentUser:
    user = user_session.get_user(party_id=party_id)

    if user is None:
        return CurrentUser.create_anonymous()

    permissions = get_permissions_for_user(user.id)

    if not required_permissions.issubset(permissions):
        return CurrentUser.create_anonymous()

    return CurrentUser.create_from_user(user, permissions)
