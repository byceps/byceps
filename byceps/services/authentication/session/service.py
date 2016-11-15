# -*- coding: utf-8 -*-

"""
byceps.services.authentication.session.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import uuid4

from ..exceptions import AuthenticationFailed

from .models import SessionToken


def create_session_token(user_id, created_at):
    """Create, but do not persist, a session token entity."""
    token = _generate_auth_token()

    return SessionToken(token, user_id, created_at)


def update_session_token(session_token, updated_at):
    """Update, but do not persist, the session token entity."""
    session_token.token = _generate_auth_token()
    session_token.created_at = updated_at


def _generate_auth_token():
    """Generate an authentication token."""
    return uuid4()


def find_session_token(token):
    """Return the session token with that ID, or `None` if not found."""
    return SessionToken.query.get(token)


def find_session_token_for_user(user_id):
    """Return the session token for the user with that ID, or `None` if
    not found.
    """
    return SessionToken.query \
        .filter_by(user_id=user_id) \
        .one_or_none()


def authenticate_session(user_id, auth_token):
    """Check the client session's validity.

    Return nothing on success, or raise an exception on failure.
    """
    if user_id is None:
        # User ID must not be empty.
        raise AuthenticationFailed()

    if not auth_token:
        # Authentication token must not be empty.
        raise AuthenticationFailed()

    session_token = find_session_token(auth_token)

    if session_token is None:
        # Session token is unknown.
        raise AuthenticationFailed()

    if user_id != session_token.user_id:
        # The user ID provided by the client does not match the server's.
        raise AuthenticationFailed()
