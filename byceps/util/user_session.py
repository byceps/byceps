"""
byceps.util.user_session
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from uuid import UUID

from flask import session

from ..services.authentication.session.models.current_user import CurrentUser
from ..services.authentication.session import service as session_service
from ..services.user import service as user_service
from ..services.user.transfer.models import User
from ..typing import PartyID, UserID

from .authorization import get_permissions_for_user


KEY_LOCALE = 'locale'
KEY_USER_ID = 'user_id'
KEY_USER_AUTH_TOKEN = 'user_auth_token'


def start(user_id: UserID, auth_token: str, *, permanent: bool = False) -> None:
    """Initialize the user's session by putting the relevant data
    into the session cookie.
    """
    session.clear()

    session[KEY_USER_ID] = str(user_id)
    session[KEY_USER_AUTH_TOKEN] = str(auth_token)
    session.permanent = permanent


def end() -> None:
    """End the user's session by deleting the session cookie."""
    session.pop(KEY_USER_ID, None)
    session.pop(KEY_USER_AUTH_TOKEN, None)
    session.permanent = False


def get_current_user(
    required_permissions: set[Enum],
    *,
    party_id: Optional[PartyID] = None,
) -> CurrentUser:
    locale = _get_locale()

    user = _find_user(party_id=party_id)

    if user is None:
        return session_service.get_anonymous_current_user(locale=locale)

    permissions = get_permissions_for_user(user.id)

    if not required_permissions.issubset(permissions):
        return session_service.get_anonymous_current_user(locale=locale)

    return session_service.get_authenticated_current_user(
        user, permissions=permissions, locale=locale
    )


def _find_user(*, party_id: Optional[PartyID] = None) -> Optional[User]:
    """Return the current user if authenticated, `None` if not.

    Return `None` if:
    - the ID is unknown.
    - the account is not enabled.
    - the auth token is invalid.
    """
    user_id_str = session.get(KEY_USER_ID)
    auth_token = session.get(KEY_USER_AUTH_TOKEN)

    if user_id_str is None:
        return None

    try:
        user_id = UserID(UUID(user_id_str))
    except ValueError:
        return None

    user = user_service.find_active_user(
        user_id, include_avatar=True, include_orga_flag_for_party_id=party_id
    )

    if user is None:
        return None

    # Validate auth token.
    if (auth_token is None) or not session_service.is_session_valid(
        user.id, auth_token
    ):
        # Bad auth token, not logging in.
        return None

    return user


def _get_locale() -> Optional[str]:
    """Return the locale set in the session, if any."""
    return session.get(KEY_LOCALE)


def set_locale(locale: str) -> None:
    """Set locale for the session."""
    session[KEY_LOCALE] = locale
