# -*- coding: utf-8 -*-

"""
byceps.blueprints.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import uuid4

from flask import url_for
from werkzeug.security import check_password_hash as _check_password_hash, \
    generate_password_hash as _generate_password_hash

from ...database import db
from ...services import email as email_service

from ..verification_token import service as verification_token_service

from .models import Credential, SessionToken


PASSWORD_HASH_ITERATIONS = 50000
PASSWORD_HASH_METHOD = 'pbkdf2:sha1:%d' % PASSWORD_HASH_ITERATIONS


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

    session_token = SessionToken(token, user.id, now)
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

    session_token = find_session_token_for_user(user.id)
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

    session_token = find_session_token(auth_token)

    if session_token is None:
        # Session token is unknown.
        raise AuthenticationFailed()

    if user_id != session_token.user_id:
        # The user ID provided by the client does not match the server's.
        raise AuthenticationFailed()


# -------------------------------------------------------------------- #
# password reset


def prepare_password_reset(user):
    """Create a verification token for password reset and email it to
    the user's address.
    """
    verification_token = verification_token_service.build_for_password_reset(user)

    db.session.add(verification_token)
    db.session.commit()

    _send_password_reset_email(user, verification_token)


def _send_password_reset_email(user, verification_token):
    confirmation_url = url_for('user.password_reset_form',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, so kannst du ein neues Passwort festlegen' \
        .format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'du kannst ein neues Passwort festlegen indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    email_service.send(subject=subject, body=body, recipients=recipients)


def reset_password(verification_token, password):
    """Reset the user's password."""
    user = verification_token.user

    db.session.delete(verification_token)
    db.session.commit()

    update_password_hash(user, password)
