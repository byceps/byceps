"""
byceps.services.authentication.password.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from werkzeug.security import check_password_hash as _check_password_hash, \
    generate_password_hash as _generate_password_hash

from ....database import db
from ....typing import UserID

from ..session import service as session_service

from .models import Credential


PASSWORD_HASH_ITERATIONS = 100000
PASSWORD_HASH_METHOD = 'pbkdf2:sha256:%d' % PASSWORD_HASH_ITERATIONS


def generate_password_hash(password: str) -> str:
    """Generate a salted hash value based on the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)


def create_password_hash(user_id: UserID, password: str) -> None:
    """Create a password-based credential and a session token for the user."""
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = Credential(user_id, password_hash, now)
    db.session.add(credential)

    session_token = session_service.create_session_token(user_id, now)
    db.session.add(session_token)

    db.session.commit()


def update_password_hash(user_id: UserID, password: str) -> None:
    """Update the password hash and set a newly-generated authentication
    token for the user.
    """
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = Credential.query.get(user_id)

    credential.password_hash = password_hash
    credential.updated_at = now

    session_token = session_service.find_session_token_for_user(user_id)
    if session_token:
        session_service.update_session_token(session_token, now)
    else:
        # No session token is stored for the user, so create a new one
        # to login with.
        session_token = session_service.create_session_token(user_id, now)
        db.session.add(session_token)

    db.session.commit()


def is_password_valid_for_user(user_id: UserID, password: str) -> bool:
    """Return `True` if the password is valid for the user, or `False`
    otherwise.
    """
    credential = Credential.query.get(user_id)

    if credential is None:
        # no password stored for user
        return False

    return check_password_hash(credential.password_hash, password)


def check_password_hash(password_hash: str, password: str) -> bool:
    """Hash the password and return `True` if the result matches the
    given hash, `False` otherwise.
    """
    return (password_hash is not None) \
        and _check_password_hash(password_hash, password)
