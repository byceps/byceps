# -*- coding: utf-8 -*-

"""
byceps.blueprints.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from werkzeug.security import generate_password_hash as _generate_password_hash

from ..user.models.user import AnonymousUser, User


PASSWORD_HASH_ITERATIONS = 50000
PASSWORD_HASH_METHOD = 'pbkdf2:sha1:%d' % PASSWORD_HASH_ITERATIONS


def generate_password_hash(password):
    """Generate a salted hash value based on the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)


class AuthenticationFailed(Exception):
    pass


def authenticate(screen_name, password):
    """Try to authenticate the user.

    Return the associated user object on success, or raise an exception
    on failure.
    """
    user = User.query.filter_by(screen_name=screen_name).first()

    if user is None:
        # User name is unknown.
        raise AuthenticationFailed()

    if not user.is_password_valid(password):
        # Password does not match.
        raise AuthenticationFailed()

    if not user.is_active:
        # User account is disabled.
        raise AuthenticationFailed()

    return user


def load_user(id, auth_token):
    """Load the user with that ID.

    Fall back to the anonymous user if the ID is unknown, the account is
    not enabled, or the auth token is invalid.
    """
    if id is None:
        return AnonymousUser()

    user = User.query.get(id)
    if (user is None) or not user.enabled:
        return AnonymousUser()

    # Validate auth token.
    if not auth_token or auth_token != str(user.auth_token):
        # Bad auth token, not logging in.
        return AnonymousUser()

    return user
