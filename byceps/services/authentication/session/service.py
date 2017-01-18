# -*- coding: utf-8 -*-

"""
byceps.services.authentication.session.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
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

    if not _is_token_valid_for_user(auth_token, user_id):
        # Session token is unknown or the user ID provided by the
        # client does not match the one stored on the server.
        raise AuthenticationFailed()


def _is_token_valid_for_user(token, user_id):
    """Return `True` if a session token with that ID exists for that user."""
    if not user_id:
        raise ValueError('User ID is invalid.')

    session_token = SessionToken.query.get(token)

    return (session_token is not None) and (session_token.user_id == user_id)
