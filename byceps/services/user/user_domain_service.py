"""
byceps.services.user.user_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime
from typing import Any

from byceps.services.user.log import user_log_serialization_service
from byceps.services.user.log.models import UserLogEntry
from byceps.util.result import Err, Ok, Result

from .errors import NothingChangedError
from .events import (
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserScreenNameChangedEvent,
)
from .models.user import User, UserDetailDifference


def suspend_account(
    user: User, initiator: User, reason: str
) -> tuple[UserAccountSuspendedEvent, UserLogEntry]:
    """Suspend the user account."""
    occurred_at = datetime.utcnow()

    event = _build_account_suspended_event(occurred_at, initiator, user, reason)

    log_entry = (
        user_log_serialization_service.serialize_account_suspended_event(event)
    )

    return event, log_entry


def _build_account_suspended_event(
    occurred_at: datetime, initiator: User, user: User, reason: str
) -> UserAccountSuspendedEvent:
    return UserAccountSuspendedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        reason=reason,
    )


def unsuspend_account(
    user: User, initiator: User, reason: str
) -> tuple[UserAccountUnsuspendedEvent, UserLogEntry]:
    """Unsuspend the user account."""
    occurred_at = datetime.utcnow()

    event = _build_account_unsuspended_event(
        occurred_at, initiator, user, reason
    )

    log_entry = (
        user_log_serialization_service.serialize_account_unsuspended_event(
            event
        )
    )

    return event, log_entry


def _build_account_unsuspended_event(
    occurred_at: datetime, initiator: User, user: User, reason: str
) -> UserAccountUnsuspendedEvent:
    return UserAccountUnsuspendedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        reason=reason,
    )


def delete_account(
    user: User,
    initiator: User,
    reason: str,
) -> tuple[UserAccountDeletedEvent, UserLogEntry]:
    """Delete the user account."""
    occurred_at = datetime.utcnow()

    event = _build_account_deleted_event(occurred_at, initiator, user, reason)

    log_entry = user_log_serialization_service.serialize_account_deleted_event(
        event
    )

    return event, log_entry


def _build_account_deleted_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
    reason: str,
) -> UserAccountDeletedEvent:
    return UserAccountDeletedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        reason=reason,
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
        occurred_at, initiator, user, old_screen_name, new_screen_name, reason
    )

    log_entry = (
        user_log_serialization_service.serialize_screen_name_changed_event(
            event
        )
    )

    return event, log_entry


def _build_screen_name_changed_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
    old_screen_name: str | None,
    new_screen_name: str | None,
    reason: str | None,
) -> UserScreenNameChangedEvent:
    return UserScreenNameChangedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        old_screen_name=old_screen_name,
        new_screen_name=new_screen_name,
        reason=reason,
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

    match _determine_details_difference(
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
        case Ok(fields):
            pass
        case Err(e):
            return Err(e)

    event = _build_details_updated_event(occurred_at, initiator, user, fields)

    log_entry = user_log_serialization_service.serialize_details_updated_event(
        event
    )

    return Ok((event, log_entry))


def _build_details_updated_event(
    occurred_at: datetime,
    initiator: User,
    user: User,
    fields: dict[str, UserDetailDifference],
) -> UserDetailsUpdatedEvent:
    return UserDetailsUpdatedEvent(
        occurred_at=occurred_at,
        initiator=initiator,
        user=user,
        fields=fields,
    )


def _determine_details_difference(
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
) -> Result[dict[str, UserDetailDifference], NothingChangedError]:
    fields: dict[str, UserDetailDifference] = {}

    def _add_if_different(
        property_key: str,
        old_value: Any | None,
        new_value: Any | None,
    ) -> None:
        if old_value != new_value:
            fields[property_key] = UserDetailDifference(
                old=_to_str_if_not_none(old_value),
                new=_to_str_if_not_none(new_value),
            )

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

    return Ok(fields)


def _to_str_if_not_none(value: Any) -> str | None:
    return str(value) if (value is not None) else None
