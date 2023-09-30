"""
byceps.services.user.user_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from byceps.events.user import (
    UserAccountCreatedEvent,
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserEmailAddressConfirmedEvent,
    UserEmailAddressInvalidatedEvent,
    UserScreenNameChangedEvent,
)
from byceps.services.site.models import SiteID
from byceps.typing import UserID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid4, generate_uuid7

from .errors import (
    AccountAlreadyInitializedError,
    InvalidEmailAddressError,
    InvalidScreenNameError,
)
from .models.log import UserLogEntry, UserLogEntryData
from .models.user import User, UserEmailAddress


def create_account(
    screen_name: str | None,
    email_address: str | None,
    password: str,
    *,
    locale: str | None = None,
    creation_method: str | None = None,
    site_id: SiteID | None = None,
    site_title: str | None = None,
    ip_address: str | None = None,
    initiator: User | None = None,
) -> Result[
    tuple[User, str | None, UserAccountCreatedEvent, UserLogEntry],
    InvalidScreenNameError | InvalidEmailAddressError,
]:
    """Create a user account."""
    occurred_at = datetime.utcnow()
    user_id = UserID(generate_uuid4())

    normalized_screen_name: str | None
    if screen_name is not None:
        screen_name_normalization_result = normalize_screen_name(screen_name)

        if screen_name_normalization_result.is_err():
            return Err(screen_name_normalization_result.unwrap_err())

        normalized_screen_name = screen_name_normalization_result.unwrap()
    else:
        normalized_screen_name = None

    normalized_email_address: str | None
    if email_address is not None:
        email_address_normalization_result = normalize_email_address(
            email_address
        )

        if email_address_normalization_result.is_err():
            return Err(email_address_normalization_result.unwrap_err())

        normalized_email_address = email_address_normalization_result.unwrap()
    else:
        normalized_email_address = None

    user = User(
        id=user_id,
        screen_name=normalized_screen_name,
        initialized=False,
        suspended=False,
        deleted=False,
        locale=locale,
        avatar_url=None,
    )

    event = _build_account_created_event(
        occurred_at, initiator, user, site_id, site_title
    )

    log_entry = _build_account_created_log_entry(
        occurred_at, initiator, user, creation_method, site_id, ip_address
    )

    return Ok((user, normalized_email_address, event, log_entry))


def _build_account_created_event(
    occurred_at: datetime,
    initiator: User | None,
    user: User,
    site_id: SiteID | None = None,
    site_title: str | None = None,
) -> UserAccountCreatedEvent:
    return UserAccountCreatedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        user_id=user.id,
        user_screen_name=user.screen_name,
        site_id=site_id,
        site_title=site_title,
    )


def _build_account_created_log_entry(
    occurred_at: datetime,
    initiator: User | None,
    user: User,
    creation_method: str | None,
    site_id: SiteID | None,
    ip_address: str | None,
) -> UserLogEntry:
    data = {}

    if initiator is not None:
        data['initiator_id'] = str(initiator.id)

    if creation_method:
        data['creation_method'] = creation_method

    if site_id:
        data['site_id'] = site_id

    if ip_address:
        data['ip_address'] = ip_address

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-created',
        user_id=user.id,
        initiator_id=initiator.id if initiator else None,
        data=data,
    )


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
        initiator_id=initiator.id if initiator else None,
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
        initiator_id=initiator.id,
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
        initiator_id=initiator.id,
        data={
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
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
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _build_account_deleted_log_entry(
    occurred_at: datetime,
    initiator: User,
    user: User,
    reason: str,
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-deleted',
        user_id=user.id,
        initiator_id=initiator.id,
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
        initiator_id=initiator.id,
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
        initiator_id=initiator.id,
        data=data,
    )


def confirm_email_address(
    user: User,
    current_email_address: UserEmailAddress,
    email_address_to_confirm: str,
) -> Result[tuple[UserEmailAddressConfirmedEvent, UserLogEntry], str]:
    """Confirm the e-mail address of the user account."""
    if current_email_address.address is None:
        return Err('Account has no email address assigned.')

    if current_email_address.address != email_address_to_confirm:
        return Err('Email addresses do not match.')

    if current_email_address.verified:
        return Err('Email address is already verified.')

    occurred_at = datetime.utcnow()

    event = _build_email_address_confirmed_event(occurred_at, user)

    log_entry = _build_email_address_confirmed_log_entry(
        occurred_at, user, email_address_to_confirm
    )

    return Ok((event, log_entry))


def _build_email_address_confirmed_event(
    occurred_at: datetime,
    user: User,
) -> UserEmailAddressConfirmedEvent:
    return UserEmailAddressConfirmedEvent(
        occurred_at=occurred_at,
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _build_email_address_confirmed_log_entry(
    occurred_at: datetime,
    user: User,
    email_address: str,
) -> UserLogEntry:
    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-email-address-confirmed',
        user_id=user.id,
        initiator_id=user.id,
        data={'email_address': email_address},
    )


def invalidate_email_address(
    user: User,
    email_address: UserEmailAddress,
    reason: str,
    *,
    initiator: User | None = None,
) -> Result[tuple[UserEmailAddressInvalidatedEvent, UserLogEntry], str]:
    """Invalidate the user's email address."""
    if email_address.address is None:
        return Err('Account has no email address assigned.')

    if not email_address.verified:
        return Err('Email address is not verified.')

    occurred_at = datetime.utcnow()

    event = _build_email_address_invalidated_event(occurred_at, initiator, user)

    log_entry = _build_email_address_invalidated_log_entry(
        occurred_at, initiator, user, email_address.address, reason
    )

    return Ok((event, log_entry))


def _build_email_address_invalidated_event(
    occurred_at: datetime,
    initiator: User | None,
    user: User,
) -> UserEmailAddressInvalidatedEvent:
    return UserEmailAddressInvalidatedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _build_email_address_invalidated_log_entry(
    occurred_at: datetime,
    initiator: User | None,
    user: User,
    email_address: str | None,
    reason: str,
) -> UserLogEntry:
    data = {
        'email_address': email_address,
        'reason': reason,
    }

    if initiator:
        data['initiator_id'] = str(initiator.id)

    return UserLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='user-email-address-invalidated',
        user_id=user.id,
        initiator_id=initiator.id if initiator else None,
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
        initiator_id=initiator.id,
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


def normalize_screen_name(
    screen_name: str,
) -> Result[str, InvalidScreenNameError]:
    """Normalize the screen name."""
    normalized = screen_name.strip()

    if not normalized or (' ' in normalized) or ('@' in normalized):
        return Err(InvalidScreenNameError(value=screen_name))

    return Ok(normalized)


def normalize_email_address(
    email_address: str,
) -> Result[str, InvalidEmailAddressError]:
    """Normalize the e-mail address."""
    normalized = email_address.strip().lower()

    if not normalized or (' ' in normalized) or ('@' not in normalized):
        return Err(InvalidEmailAddressError(value=email_address))

    return Ok(normalized)
