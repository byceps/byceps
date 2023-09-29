"""
byceps.services.authn.password.authn_password_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from werkzeug.security import (
    check_password_hash as _werkzeug_check_password_hash,
    generate_password_hash as _werkzeug_generate_password_hash,
)

from byceps.events.authn import PasswordUpdatedEvent
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User
from byceps.typing import UserID
from byceps.util.uuid import generate_uuid7

from .models import Credential


# https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pbkdf2
_PASSWORD_HASH_ITERATIONS = 600000
_PASSWORD_HASH_METHOD = 'pbkdf2:sha256:%d' % _PASSWORD_HASH_ITERATIONS


def _generate_password_hash(password: str) -> str:
    """Generate a salted hash value based on the password."""
    return _werkzeug_generate_password_hash(
        password, method=_PASSWORD_HASH_METHOD
    )


def create_password_hash(user_id: UserID, password: str) -> Credential:
    """Create a password-based credential for the user."""
    return Credential(
        user_id=user_id,
        password_hash=_generate_password_hash(password),
        updated_at=datetime.utcnow(),
    )


def update_password_hash(
    user: User, password: str, initiator: User
) -> tuple[Credential, PasswordUpdatedEvent, UserLogEntry]:
    """Update a password hash."""
    credential = create_password_hash(user.id, password)

    event = _build_password_updated_event(
        credential.updated_at, initiator, user
    )

    log_entry = _build_password_updated_log_entry(
        credential.updated_at, initiator, user
    )

    return credential, event, log_entry


def _build_password_updated_event(
    occurred_at: datetime, initiator: User, user: User
) -> PasswordUpdatedEvent:
    return PasswordUpdatedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _build_password_updated_log_entry(
    occurred_at: datetime, initiator: User, user: User
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='password-updated',
        user_id=user.id,
        data={'initiator_id': str(initiator.id)},
    )


def check_password_hash(password_hash: str, password: str) -> bool:
    """Hash the password and return `True` if the result matches the
    given hash, `False` otherwise.
    """
    return (password_hash is not None) and _werkzeug_check_password_hash(
        password_hash, password
    )


def is_password_hash_current(password_hash: str) -> bool:
    """Return `True` if the password hash was created with the currently
    configured method (algorithm and parameters).
    """
    return password_hash.startswith(_PASSWORD_HASH_METHOD + '$')
