"""
byceps.services.user.user_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime
from typing import Any

from byceps.util.result import Err, Ok, Result

from . import user_log_domain_service
from .errors import NothingChangedError
from .events import (
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserScreenNameChangedEvent,
)
from .models.log import UserLogEntry
from .models.user import User


def suspend_account(
    user: User, initiator: User, reason: str
) -> tuple[UserAccountSuspendedEvent, UserLogEntry]:
    """Suspend the user account."""
    occurred_at = datetime.utcnow()

    event = _build_account_suspended_event(occurred_at, initiator, user)

    log_entry = _build_account_suspended_log_entry(
        occurred_at, initiator, user, reason
    )

    return event, log_entry


def _build_account_suspended_event(
    occurred_at: datetime, initiator: User, user: User
) -> UserAccountSuspendedEvent:
    return UserAccountSuspendedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
    )


def _build_account_suspended_log_entry(
    occurred_at: datetime, initiator: User, user: User, reason: str
) -> UserLogEntry:
    return user_log_domain_service.build_entry(
        'user-suspended',
        user,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
        occurred_at=occurred_at,
        initiator=initiator,
    )


def unsuspend_account(
    user: User, initiator: User, reason: str
) -> tuple[UserAccountUnsuspendedEvent, UserLogEntry]:
    """Unsuspend the user account."""
    occurred_at = datetime.utcnow()

    event = _build_account_unsuspended_event(occurred_at, initiator, user)

    log_entry = _build_account_unsuspended_log_entry(
        occurred_at, initiator, user, reason
    )

    return event, log_entry


def _build_account_unsuspended_event(
    occurred_at: datetime, initiator: User, user: User
) -> UserAccountUnsuspendedEvent:
    return UserAccountUnsuspendedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
    )


def _build_account_unsuspended_log_entry(
    occurred_at: datetime, initiator: User, user: User, reason: str
) -> UserLogEntry:
    return user_log_domain_service.build_entry(
        'user-unsuspended',
        user,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
        occurred_at=occurred_at,
        initiator=initiator,
    )


def delete_account(
    user: User,
    initiator: User,
    reason: str,
) -> tuple[UserAccountDeletedEvent, UserLogEntry]:
    """Delete the user account."""
    occurred_at = datetime.utcnow()

    event = _build_account_deleted_event(occurred_at, initiator, user)

    log_entry = _build_account_deleted_log_entry(
        occurred_at, initiator, user, reason
    )

    return event, log_entry


def _build_account_deleted_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
) -> UserAccountDeletedEvent:
    return UserAccountDeletedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
    )


def _build_account_deleted_log_entry(
    occurred_at: datetime,
    initiator: User,
    user: User,
    reason: str,
) -> UserLogEntry:
    return user_log_domain_service.build_entry(
        'user-deleted',
        user,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
        occurred_at=occurred_at,
        initiator=initiator,
    )


def change_screen_name(
    user: User,
    new_screen_name: str,
    initiator: User,
    *,
    reason: str | None = None,
) -> tuple[UserScreenNameChangedEvent, UserLogEntry]:
    """Change the user's screen name."""
    occurred_at = datetime.utcnow()
    old_screen_name = user.screen_name

    event = _build_screen_name_changed_event(
        occurred_at, initiator, user, old_screen_name, new_screen_name
    )

    log_entry = _build_screen_name_changed_log_entry(
        occurred_at, initiator, user, old_screen_name, new_screen_name, reason
    )

    return event, log_entry


def _build_screen_name_changed_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
    old_screen_name: str | None,
    new_screen_name: str | None,
) -> UserScreenNameChangedEvent:
    return UserScreenNameChangedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user_id=user.id,
        old_screen_name=old_screen_name,
        new_screen_name=new_screen_name,
    )


def _build_screen_name_changed_log_entry(
    occurred_at: datetime,
    initiator: User,
    user: User,
    old_screen_name: str | None,
    new_screen_name: str | None,
    reason: str | None,
) -> UserLogEntry:
    data = {
        'initiator_id': str(initiator.id),
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
    }

    if reason:
        data['reason'] = reason

    return user_log_domain_service.build_entry(
        'user-screen-name-changed',
        user,
        data,
        occurred_at=occurred_at,
        initiator=initiator,
    )


def update_details(
    user: User,
    old_first_name: str | None,
    new_first_name: str | None,
    old_last_name: str | None,
    new_last_name: str | None,
    old_date_of_birth: date | None,
    new_date_of_birth: date | None,
    old_country: str | None,
    new_country: str | None,
    old_postal_code: str | None,
    new_postal_code: str | None,
    old_city: str | None,
    new_city: str | None,
    old_street: str | None,
    new_street: str | None,
    old_phone_number: str | None,
    new_phone_number: str | None,
    initiator: User,
) -> Result[tuple[UserDetailsUpdatedEvent, UserLogEntry], NothingChangedError]:
    """Update the user's details."""
    occurred_at = datetime.utcnow()

    event = _build_details_updated_event(occurred_at, initiator, user)

    match _build_details_updated_log_entry(
        occurred_at,
        initiator,
        user,
        old_first_name,
        new_first_name,
        old_last_name,
        new_last_name,
        old_date_of_birth,
        new_date_of_birth,
        old_country,
        new_country,
        old_postal_code,
        new_postal_code,
        old_city,
        new_city,
        old_street,
        new_street,
        old_phone_number,
        new_phone_number,
    ):
        case Ok(log_entry):
            return Ok((event, log_entry))
        case Err(e):
            return Err(e)


def _build_details_updated_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
) -> UserDetailsUpdatedEvent:
    return UserDetailsUpdatedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
    )


def _build_details_updated_log_entry(
    occurred_at: datetime,
    initiator: User,
    user: User,
    old_first_name: str | None,
    new_first_name: str | None,
    old_last_name: str | None,
    new_last_name: str | None,
    old_date_of_birth: date | None,
    new_date_of_birth: date | None,
    old_country: str | None,
    new_country: str | None,
    old_postal_code: str | None,
    new_postal_code: str | None,
    old_city: str | None,
    new_city: str | None,
    old_street: str | None,
    new_street: str | None,
    old_phone_number: str | None,
    new_phone_number: str | None,
) -> Result[UserLogEntry, NothingChangedError]:
    fields: dict[str, dict[str, str | None]] = {}

    def _add_if_different(
        property_key: str,
        old_value: Any | None,
        new_value: Any | None,
    ) -> None:
        if old_value != new_value:
            fields[property_key] = {
                'old': _to_str_if_not_none(old_value),
                'new': _to_str_if_not_none(new_value),
            }

    _add_if_different('first_name', old_first_name, new_first_name)
    _add_if_different('last_name', old_last_name, new_last_name)
    _add_if_different('date_of_birth', old_date_of_birth, new_date_of_birth)
    _add_if_different('country', old_country, new_country)
    _add_if_different('postal_code', old_postal_code, new_postal_code)
    _add_if_different('city', old_city, new_city)
    _add_if_different('street', old_street, new_street)
    _add_if_different('phone_number', old_phone_number, new_phone_number)

    if not fields:
        return Err(NothingChangedError())

    data = {
        'fields': fields,
        'initiator_id': str(initiator.id),
    }

    entry = user_log_domain_service.build_entry(
        'user-details-updated',
        user,
        data,
        occurred_at=occurred_at,
        initiator=initiator,
    )

    return Ok(entry)


def _to_str_if_not_none(value: Any) -> str | None:
    return str(value) if (value is not None) else None
