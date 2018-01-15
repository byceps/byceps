"""
byceps.blueprints.authentication.session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Union

from flask import session

from ...services.authentication.exceptions import AuthenticationFailed
from ...services.authentication.session import service as session_service
from ...services.user.models.user import AnonymousUser, User
from ...services.user import service as user_service
from ...typing import UserID


KEY_USER_ID = 'user_id'
KEY_USER_AUTH_TOKEN = 'user_auth_token'


def start(user_id: UserID, auth_token: str, *, permanent: bool=False) -> None:
    """Initialize the user's session by putting the relevant data
    into the session cookie.
    """
    session[KEY_USER_ID] = str(user_id)
    session[KEY_USER_AUTH_TOKEN] = str(auth_token)
    session.permanent = permanent


def end() -> None:
    """End the user's session by deleting the session cookie."""
    session.pop(KEY_USER_ID, None)
    session.pop(KEY_USER_AUTH_TOKEN, None)
    session.permanent = False


def get_user() -> Union[AnonymousUser, User]:
    """Return the current user, falling back to the anonymous user."""
    return _load_user(_get_user_id(), _get_auth_token())


def _get_user_id() -> Optional[str]:
    """Return the current user's ID, or `None` if not available."""
    return session.get(KEY_USER_ID)


def _get_auth_token() -> Optional[str]:
    """Return the current user's auth token, or `None` if not available."""
    return session.get(KEY_USER_AUTH_TOKEN)


def _load_user(user_id: str, auth_token: str) -> Union[AnonymousUser, User]:
    """Load the user with that ID.

    Fall back to the anonymous user if the ID is unknown, the account is
    not enabled, or the auth token is invalid.
    """
    if user_id is None:
        return user_service.get_anonymous_user()

    user = user_service.find_user(user_id)

    if (user is None) or not user.enabled:
        return user_service.get_anonymous_user()

    # Validate auth token.
    if not _is_auth_token_valid(user.id, auth_token):
        # Bad auth token, not logging in.
        return user_service.get_anonymous_user()

    return user


def _is_auth_token_valid(user_id: UserID, auth_token) -> bool:
    try:
        session_service.authenticate_session(user_id, auth_token)
    except AuthenticationFailed:
        return False
    else:
        return True
