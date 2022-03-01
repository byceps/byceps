"""
byceps.services.authentication.password.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from werkzeug.security import (
    check_password_hash as _check_password_hash,
    generate_password_hash as _generate_password_hash,
)

from ....database import db
from ....typing import UserID

from ...user import log_service as user_log_service

from ..session import service as session_service

from .dbmodels import Credential as DbCredential


PASSWORD_HASH_ITERATIONS = 320000
PASSWORD_HASH_METHOD = 'pbkdf2:sha256:%d' % PASSWORD_HASH_ITERATIONS


def generate_password_hash(password: str) -> str:
    """Generate a salted hash value based on the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)


def create_password_hash(user_id: UserID, password: str) -> None:
    """Create a password-based credential and a session token for the user."""
    password_hash = generate_password_hash(password)
    now = datetime.utcnow()

    credential = DbCredential(user_id, password_hash, now)
    db.session.add(credential)
    db.session.commit()


def update_password_hash(
    user_id: UserID, password: str, initiator_id: UserID
) -> None:
    """Update the password hash and set a newly-generated authentication
    token for the user.
    """
    credential = _get_credential_for_user(user_id)

    credential.password_hash = generate_password_hash(password)
    credential.updated_at = datetime.utcnow()

    log_entry = user_log_service.build_log_entry(
        'password-updated',
        user_id,
        {
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    db.session.commit()

    session_service.delete_session_tokens_for_user(user_id)


def is_password_valid_for_user(user_id: UserID, password: str) -> bool:
    """Return `True` if the password is valid for the user, or `False`
    otherwise.
    """
    credential = _find_credential_for_user(user_id)

    if credential is None:
        # no password stored for user
        return False

    return check_password_hash(credential.password_hash, password)


def check_password_hash(password_hash: str, password: str) -> bool:
    """Hash the password and return `True` if the result matches the
    given hash, `False` otherwise.
    """
    return (password_hash is not None) and _check_password_hash(
        password_hash, password
    )


def migrate_password_hash_if_outdated(user_id: UserID, password: str) -> None:
    """Recreate the password hash with the current algorithm and parameters."""
    credential = _get_credential_for_user(user_id)

    if is_password_hash_current(credential.password_hash):
        return

    credential.password_hash = generate_password_hash(password)
    credential.updated_at = datetime.utcnow()
    db.session.commit()


def is_password_hash_current(password_hash: str) -> bool:
    """Return `True` if the password hash was created with the currently
    configured method (algorithm and parameters).
    """
    return password_hash.startswith(PASSWORD_HASH_METHOD + '$')


def _find_credential_for_user(user_id: UserID) -> Optional[DbCredential]:
    """Return the credential for the user, if found."""
    return db.session.get(DbCredential, user_id)


def _get_credential_for_user(user_id: UserID) -> DbCredential:
    """Return the credential for the user, or raise exception if not found."""
    credential = _find_credential_for_user(user_id)

    if credential is None:
        raise Exception(f'No credential found for user ID "{user_id}"')

    return credential


def delete_password_hash(user_id: UserID) -> None:
    """Delete user's credentials."""
    db.session.query(DbCredential) \
        .filter_by(user_id=user_id) \
        .delete()

    db.session.commit()
