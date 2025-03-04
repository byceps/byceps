"""
byceps.services.user.user_email_address_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.core.events import EventUser
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .events import (
    UserEmailAddressChangedEvent,
    UserEmailAddressConfirmedEvent,
    UserEmailAddressInvalidatedEvent,
)
from .models.log import UserLogEntry
from .models.user import User, UserEmailAddress


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
        initiator=EventUser.from_user(initiator),
        user=EventUser.from_user(user),
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
        initiator=EventUser.from_user(user),
        user=EventUser.from_user(user),
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
        initiator=EventUser.from_user(initiator) if initiator else None,
        user=EventUser.from_user(user),
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
