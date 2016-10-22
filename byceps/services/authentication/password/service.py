# -*- coding: utf-8 -*-

"""
byceps.services.authentication.password.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from werkzeug.security import check_password_hash as _check_password_hash, \
    generate_password_hash as _generate_password_hash

from ....database import db

from ..session import service as session_service

from .models import Credential


PASSWORD_HASH_ITERATIONS = 100000
PASSWORD_HASH_METHOD = 'pbkdf2:sha256:%d' % PASSWORD_HASH_ITERATIONS


def generate_password_hash(password):
    """Generate a salted hash value based on the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)


def create_password_hash(user_id, password):
    """Create a password-based credential for the user."""
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = Credential(user_id, password_hash, now)
    db.session.add(credential)

    session_token = session_service.create_session_token(user_id, now)
    db.session.add(session_token)

    db.session.commit()


def update_password_hash(user_id, password):
    """Update the password hash and set a newly-generated authentication
    token for the user.
    """
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = Credential.query.get(user_id)

    credential.password_hash = password_hash
    credential.updated_at = now

    session_token = session_service.find_session_token_for_user(user_id)
    session_service.update_session_token(session_token, now)

    db.session.commit()


def is_password_valid_for_user(user_id, password):
    """Return `True` if the password is valid for the user, or `False`
    otherwise.
    """
    credential = Credential.query.get(user_id)

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
