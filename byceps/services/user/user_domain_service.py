"""
byceps.services.user.user_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from byceps.database import generate_uuid7
from byceps.events.user import (
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserScreenNameChangedEvent,
)
from byceps.services.user.models.log import UserLogEntry, UserLogEntryData
from byceps.util.result import Err, Ok, Result

from .errors import AccountAlreadyInitializedError
from .models.user import User


def initialize_account(
    user: User,
    *,
    initiator: User | None = None,
) -> Result[UserLogEntry, AccountAlreadyInitializedError]:
    """Initialize the user account."""
    if user.initialized:
        return Err(AccountAlreadyInitializedError())

    occurred_at = datetime.utcnow()

    log_entry = _build_account_initialized_log_entry(
        occurred_at, initiator, user
    )

    return Ok(log_entry)


def _build_account_initialized_log_entry(
    occurred_at: datetime, initiator: User | None, user: User
) -> UserLogEntry:
    data = {}

    if initiator:
        data['initiator_id'] = str(initiator.id)

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-initialized',
        user_id=user.id,
        data=data,
    )


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
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _build_account_suspended_log_entry(
    occurred_at: datetime, initiator: User, user: User, reason: str
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-suspended',
        user_id=user.id,
        data={
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
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
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _build_account_unsuspended_log_entry(
    occurred_at: datetime, initiator: User, user: User, reason: str
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-unsuspended',
        user_id=user.id,
        data={
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
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
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
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

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-screen-name-changed',
        user_id=user.id,
        data=data,
    )


def change_email_address(
    user: User,
    old_email_address: str | None,
    new_email_address: str | None,
    verified: bool,
    initiator: User,
    *,
    reason: str | None = None,
) -> tuple[UserEmailAddressChangedEvent, UserLogEntry]:
    """Change the user's e-mail address."""
    occurred_at = datetime.utcnow()

    event = _build_email_address_changed_event(occurred_at, initiator, user)

    log_entry = _build_email_address_changed_log_entry(
        occurred_at,
        initiator,
        user,
        old_email_address,
        new_email_address,
        reason,
    )

    return event, log_entry


def _build_email_address_changed_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
) -> UserEmailAddressChangedEvent:
    return UserEmailAddressChangedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _build_email_address_changed_log_entry(
    occurred_at: datetime,
    initiator: User,
    user: User,
    old_email_address: str | None,
    new_email_address: str | None,
    reason: str | None,
) -> UserLogEntry:
    data = {
        'initiator_id': str(initiator.id),
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
    }

    if reason:
        data['reason'] = reason

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-email-address-changed',
        user_id=user.id,
        data=data,
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
    old_zip_code: str | None,
    new_zip_code: str | None,
    old_city: str | None,
    new_city: str | None,
    old_street: str | None,
    new_street: str | None,
    old_phone_number: str | None,
    new_phone_number: str | None,
    initiator: User,
) -> tuple[UserDetailsUpdatedEvent, UserLogEntry]:
    """Update the user's details."""
    occurred_at = datetime.utcnow()

    event = _build_details_updated_event(occurred_at, initiator, user)

    log_entry = _build_details_updated_log_entry(
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
        old_zip_code,
        new_zip_code,
        old_city,
        new_city,
        old_street,
        new_street,
        old_phone_number,
        new_phone_number,
    )

    return event, log_entry


def _build_details_updated_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
) -> UserDetailsUpdatedEvent:
    return UserDetailsUpdatedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
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
    old_zip_code: str | None,
    new_zip_code: str | None,
    old_city: str | None,
    new_city: str | None,
    old_street: str | None,
    new_street: str | None,
    old_phone_number: str | None,
    new_phone_number: str | None,
) -> UserLogEntry:
    data = {
        'initiator_id': str(initiator.id),
    }

    _add_if_different(data, 'first_name', old_first_name, new_first_name)
    _add_if_different(data, 'last_name', old_last_name, new_last_name)
    _add_if_different(
        data, 'date_of_birth', old_date_of_birth, new_date_of_birth
    )
    _add_if_different(data, 'country', old_country, new_country)
    _add_if_different(data, 'zip_code', old_zip_code, new_zip_code)
    _add_if_different(data, 'city', old_city, new_city)
    _add_if_different(data, 'street', old_street, new_street)
    _add_if_different(data, 'phone_number', old_phone_number, new_phone_number)

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-details-updated',
        user_id=user.id,
        data=data,
    )


def _add_if_different(
    log_entry_data: UserLogEntryData,
    base_key_name: str,
    old_value: Any | None,
    new_value: Any | None,
) -> None:
    if old_value != new_value:
        log_entry_data[f'old_{base_key_name}'] = _to_str_if_not_none(old_value)
        log_entry_data[f'new_{base_key_name}'] = _to_str_if_not_none(new_value)


def _to_str_if_not_none(value: Any) -> str | None:
    return str(value) if (value is not None) else None
