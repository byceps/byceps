# -*- coding: utf-8 -*-

"""
byceps.blueprints.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import uuid4

from werkzeug.security import check_password_hash as _check_password_hash, \
    generate_password_hash as _generate_password_hash

from ...database import db

from .models import Credential, SessionToken


PASSWORD_HASH_ITERATIONS = 50000
PASSWORD_HASH_METHOD = 'pbkdf2:sha1:%d' % PASSWORD_HASH_ITERATIONS


def find_session_token(user_id):
    """Return the session token for the user with that id, or `None` if
    not found.
    """
    return SessionToken.query.get(user_id)


def generate_password_hash(password):
    """Generate a salted hash value based on the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)


def create_password_hash(user, password):
    """Create a password-based credential for the user."""
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = Credential(user.id, password_hash, now)
    db.session.add(credential)

    token = _generate_auth_token()

    session_token = SessionToken(user.id, token, now)
    db.session.add(session_token)

    db.session.commit()


def update_password_hash(user, password):
    """Update the password hash and set a newly-generated authentication
    token for the user.
    """
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = Credential.query.get(user.id)

    credential.password_hash = password_hash
    credential.updated_at = now

    session_token = find_session_token(user.id)
    session_token.token = _generate_auth_token()
    session_token.created_at = now

    db.session.commit()


def _generate_auth_token():
    """Generate an authentication token."""
    return uuid4()


def is_password_valid_for_user(user, password):
    """Return `True` if the password is valid for the user, or `False`
    otherwise.
    """
    credential = Credential.query.get(user.id)

    if credential is None:
        # no password stored for user
        return False

    return check_password_hash(credential.password_hash, password)


def check_password_hash(password_hash, password):
    """Hash the password and return `True` if the result matches the
    given hash, `False` otherwise.
    """
    return (password_hash is not None) \
        and _check_password_hash(password_hash, password)


class AuthenticationFailed(Exception):
    pass


def authenticate(user, password):
    """Try to authenticate the user.

    Return the user object on success, or raise an exception on failure.
    """
    if not is_password_valid_for_user(user, password):
        # Password does not match.
        raise AuthenticationFailed()

    if not user.is_active:
        # User account is disabled.
        raise AuthenticationFailed()

    return user


def authenticate_session(user_id, auth_token):
    """Check the client session's validity.

    Return the nothing on success, or raise an exception on failure.
    """
    if user_id is None:
        # User ID must not be empty.
        raise AuthenticationFailed()

    if not auth_token:
        # Authentication token must not be empty.
        raise AuthenticationFailed()

    session_token = find_session_token(user_id)

    if session_token is None:
        # Session token is unknown.
        raise AuthenticationFailed()

    if auth_token != str(session_token.token):
        # Client's token does not match the server's.
        raise AuthenticationFailed()
