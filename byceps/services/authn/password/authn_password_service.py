"""
byceps.services.authn.password.authn_password_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from secret_type import secret
from sqlalchemy import delete

from byceps.database import db
from byceps.events.authn import PasswordUpdatedEvent
from byceps.services.authn.session import authn_session_service
from byceps.services.user import user_log_service
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import Password, User, UserID

from . import authn_password_domain_service
from .dbmodels import DbCredential
from .models import Credential


def create_password_hash(user_id: UserID, password: Password) -> None:
    """Create a password-based credential and a session token for the user."""
    credential = authn_password_domain_service.create_password_hash(
        user_id, password
    )

    db_credential = DbCredential(
        credential.user_id, credential.password_hash, credential.updated_at
    )
    db.session.add(db_credential)
    db.session.commit()


def update_password_hash(
    user: User, password: Password, initiator: User
) -> PasswordUpdatedEvent:
    """Update the password hash and set a newly-generated authentication
    token for the user.
    """
    (
        credential,
        event,
        log_entry,
    ) = authn_password_domain_service.update_password_hash(
        user, password, initiator
    )

    _persist_password_hash_update(credential, log_entry)

    authn_session_service.delete_session_tokens_for_user(user.id)

    return event


def _persist_password_hash_update(
    credential: Credential, log_entry: UserLogEntry
) -> None:
    db_credential = _get_credential_for_user(credential.user_id)

    with credential.password_hash.dangerous_reveal() as password_hash:
        db_credential.password_hash = password_hash
    db_credential.updated_at = credential.updated_at

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def is_password_valid_for_user(user_id: UserID, password: Password) -> bool:
    """Return `True` if the password is valid for the user, or `False`
    otherwise.
    """
    db_credential = _find_credential_for_user(user_id)

    if db_credential is None:
        # no password stored for user
        return False

    password_hash = secret(db_credential.password_hash)
    return authn_password_domain_service.check_password_hash(
        password_hash, password
    )


def migrate_password_hash_if_outdated(
    user_id: UserID, password: Password
) -> None:
    """Recreate the password hash with the current algorithm and parameters."""
    db_credential = _get_credential_for_user(user_id)

    password_hash = secret(db_credential.password_hash)
    if authn_password_domain_service.is_password_hash_current(password_hash):
        return

    credential = authn_password_domain_service.create_password_hash(
        user_id, password
    )

    with credential.password_hash.dangerous_reveal() as password_hash:
        db_credential.password_hash = password_hash
    db_credential.updated_at = credential.updated_at
    db.session.commit()


def _find_credential_for_user(user_id: UserID) -> DbCredential | None:
    """Return the credential for the user, if found."""
    return db.session.get(DbCredential, user_id)


def _get_credential_for_user(user_id: UserID) -> DbCredential:
    """Return the credential for the user, or raise exception if not found."""
    db_credential = _find_credential_for_user(user_id)

    if db_credential is None:
        raise Exception(f'No credential found for user ID "{user_id}"')

    return db_credential


def delete_password_hash(user_id: UserID) -> None:
    """Delete user's credentials."""
    db.session.execute(
        delete(DbCredential).where(DbCredential.user_id == user_id)
    )

    db.session.commit()
