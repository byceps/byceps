"""
byceps.util.user_session
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from uuid import UUID

from babel import parse_locale
from flask import session

from byceps.services.authentication.session import authn_session_service
from byceps.services.authentication.session.models import CurrentUser
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import UserID

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


def get_current_user(required_permissions: set[str]) -> CurrentUser:
    session_locale = _get_session_locale()

    user = _find_user()
    if user is None:
        return authn_session_service.get_anonymous_current_user(session_locale)

    permissions = get_permissions_for_user(user.id)
    if not required_permissions.issubset(permissions):
        return authn_session_service.get_anonymous_current_user(session_locale)

    locale = _get_user_locale(user) or session_locale

    return authn_session_service.get_authenticated_current_user(
        user, locale, permissions
    )


def _find_user() -> User | None:
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

    user = user_service.find_active_user(user_id, include_avatar=True)

    if user is None:
        return None

    # Validate auth token.
    if (auth_token is None) or not authn_session_service.is_session_valid(
        user.id, auth_token
    ):
        # Bad auth token, not logging in.
        return None

    return user


def _get_session_locale() -> str | None:
    """Return the locale set in the session, if any."""
    return session.get(KEY_LOCALE)


def _get_user_locale(user: User) -> str | None:
    """Return the locale set for the user, if any."""
    locale_str = user.locale
    if not locale_str:
        return None

    try:
        parse_locale(locale_str)
    except ValueError:
        return None

    return locale_str


def set_locale(locale: str) -> None:
    """Set locale for the session."""
    session[KEY_LOCALE] = locale
