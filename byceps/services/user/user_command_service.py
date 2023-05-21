"""
byceps.services.user.user_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from warnings import warn

from babel import Locale
from sqlalchemy import select

from byceps.database import db
from byceps.events.user import (
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserScreenNameChangedEvent,
)
from byceps.services.authorization import authz_service
from byceps.services.authorization.models import RoleID
from byceps.typing import UserID

from . import user_log_service, user_service
from .dbmodels.detail import DbUserDetail
from .dbmodels.user import DbUser
from .models.log import UserLogEntryData
from .models.user import User


def initialize_account(
    user_id: UserID,
    *,
    initiator_id: UserID | None = None,
    assign_roles: bool = True,
) -> None:
    """Initialize the user account.

    This is meant to happen only once at most, and can not be undone.
    """
    db_user = _get_db_user(user_id)

    initiator: User | None
    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    if db_user.initialized:
        raise ValueError('Account is already initialized.')

    db_user.initialized = True

    log_entry_data = {}
    if initiator:
        log_entry_data['initiator_id'] = str(initiator.id)
    log_entry = user_log_service.build_entry(
        'user-initialized', db_user.id, log_entry_data
    )
    db.session.add(log_entry)

    db.session.commit()

    if assign_roles:
        _assign_roles(db_user.id, initiator_id=initiator_id)


def _assign_roles(
    user_id: UserID, *, initiator_id: UserID | None = None
) -> None:
    board_user_role_name = 'board_user'
    board_user_role = authz_service.find_role(RoleID(board_user_role_name))
    if board_user_role is None:
        warn(
            f'Role "{board_user_role_name}" not found; '
            f'not assigning it to user "{user_id}".',
            stacklevel=2,
        )
        return

    authz_service.assign_role_to_user(
        board_user_role.id, user_id, initiator_id=initiator_id
    )


def suspend_account(
    user_id: UserID, initiator_id: UserID, reason: str
) -> UserAccountSuspendedEvent:
    """Suspend the user account."""
    db_user = _get_db_user(user_id)
    initiator = user_service.get_user(initiator_id)
    occurred_at = datetime.utcnow()

    db_user.suspended = True

    log_entry = user_log_service.build_entry(
        'user-suspended',
        db_user.id,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
        occurred_at=occurred_at,
    )
    db.session.add(log_entry)

    db.session.commit()

    return UserAccountSuspendedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=db_user.id,
        user_screen_name=db_user.screen_name,
    )


def unsuspend_account(
    user_id: UserID, initiator_id: UserID, reason: str
) -> UserAccountUnsuspendedEvent:
    """Unsuspend the user account."""
    db_user = _get_db_user(user_id)
    initiator = user_service.get_user(initiator_id)
    occurred_at = datetime.utcnow()

    db_user.suspended = False

    log_entry = user_log_service.build_entry(
        'user-unsuspended',
        db_user.id,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
        occurred_at=occurred_at,
    )
    db.session.add(log_entry)

    db.session.commit()

    return UserAccountUnsuspendedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=db_user.id,
        user_screen_name=db_user.screen_name,
    )


def change_screen_name(
    user_id: UserID,
    new_screen_name: str,
    initiator_id: UserID,
    *,
    reason: str | None = None,
) -> UserScreenNameChangedEvent:
    """Change the user's screen name."""
    db_user = _get_db_user(user_id)
    initiator = user_service.get_user(initiator_id)
    occurred_at = datetime.utcnow()

    old_screen_name = db_user.screen_name

    db_user.screen_name = new_screen_name

    log_entry_data = {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'initiator_id': str(initiator.id),
    }
    if reason:
        log_entry_data['reason'] = reason

    log_entry = user_log_service.build_entry(
        'user-screen-name-changed',
        db_user.id,
        log_entry_data,
        occurred_at=occurred_at,
    )
    db.session.add(log_entry)

    db.session.commit()

    return UserScreenNameChangedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=db_user.id,
        old_screen_name=old_screen_name,
        new_screen_name=new_screen_name,
    )


def change_email_address(
    user_id: UserID,
    new_email_address: str | None,
    verified: bool,
    initiator_id: UserID,
    *,
    reason: str | None = None,
) -> UserEmailAddressChangedEvent:
    """Change the user's e-mail address."""
    db_user = _get_db_user(user_id)
    initiator = user_service.get_user(initiator_id)
    occurred_at = datetime.utcnow()

    old_email_address = db_user.email_address

    db_user.email_address = new_email_address
    db_user.email_address_verified = verified

    log_entry_data = {
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
        'initiator_id': str(initiator.id),
    }
    if reason:
        log_entry_data['reason'] = reason

    log_entry = user_log_service.build_entry(
        'user-email-address-changed',
        db_user.id,
        log_entry_data,
        occurred_at=occurred_at,
    )
    db.session.add(log_entry)

    db.session.commit()

    return UserEmailAddressChangedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=db_user.id,
        user_screen_name=db_user.screen_name,
    )


def update_locale(user_id: UserID, locale: Locale | None) -> None:
    """Change the user's locale."""
    db_user = _get_db_user(user_id)

    db_user.locale = locale.language if (locale is not None) else None
    db.session.commit()


def update_user_details(
    user_id: UserID,
    first_name: str,
    last_name: str,
    date_of_birth: date,
    country: str,
    zip_code,
    city: str,
    street: str,
    phone_number: str,
    initiator_id: UserID,
) -> UserDetailsUpdatedEvent:
    """Update the user's details."""
    detail = _get_user_detail(user_id)
    initiator = user_service.get_user(initiator_id)
    occurred_at = datetime.utcnow()

    old_first_name = detail.first_name
    old_last_name = detail.last_name
    old_date_of_birth = detail.date_of_birth
    old_country = detail.country
    old_zip_code = detail.zip_code
    old_city = detail.city
    old_street = detail.street
    old_phone_number = detail.phone_number

    detail.first_name = first_name
    detail.last_name = last_name
    detail.date_of_birth = date_of_birth
    detail.country = country
    detail.zip_code = zip_code
    detail.city = city
    detail.street = street
    detail.phone_number = phone_number

    log_entry_data = {
        'initiator_id': str(initiator.id),
    }
    _add_if_different(log_entry_data, 'first_name', old_first_name, first_name)
    _add_if_different(log_entry_data, 'last_name', old_last_name, last_name)
    _add_if_different(
        log_entry_data, 'date_of_birth', old_date_of_birth, date_of_birth
    )
    _add_if_different(log_entry_data, 'country', old_country, country)
    _add_if_different(log_entry_data, 'zip_code', old_zip_code, zip_code)
    _add_if_different(log_entry_data, 'city', old_city, city)
    _add_if_different(log_entry_data, 'street', old_street, street)
    _add_if_different(
        log_entry_data, 'phone_number', old_phone_number, phone_number
    )
    log_entry = user_log_service.build_entry(
        'user-details-updated',
        user_id,
        log_entry_data,
        occurred_at=occurred_at,
    )
    db.session.add(log_entry)

    db.session.commit()

    user = user_service.get_user(detail.user_id)
    return UserDetailsUpdatedEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _add_if_different(
    log_entry_data: UserLogEntryData,
    base_key_name: str,
    old_value: str,
    new_value,
) -> None:
    if old_value != new_value:
        log_entry_data[f'old_{base_key_name}'] = _to_str_if_not_none(old_value)
        log_entry_data[f'new_{base_key_name}'] = _to_str_if_not_none(new_value)


def _to_str_if_not_none(value: Any) -> str | None:
    return str(value) if (value is not None) else None


def set_user_detail_extra(user_id: UserID, key: str, value: str) -> None:
    """Set a value for a key in the user's detail extras map."""
    detail = _get_user_detail(user_id)

    if detail.extras is None:
        detail.extras = {}

    detail.extras[key] = value

    db.session.commit()


def remove_user_detail_extra(user_id: UserID, key: str) -> None:
    """Remove the entry with that key from the user's detail extras map."""
    detail = _get_user_detail(user_id)

    if (detail.extras is None) or (key not in detail.extras):
        return

    del detail.extras[key]
    db.session.commit()


def _get_db_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    return user_service.get_db_user(user_id)


def _get_user_detail(user_id: UserID) -> DbUserDetail:
    """Return the user's details, or raise an exception."""
    detail = db.session.scalars(
        select(DbUserDetail).filter_by(user_id=user_id)
    ).one_or_none()

    if detail is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return detail
