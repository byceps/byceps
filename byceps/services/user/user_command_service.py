"""
byceps.services.user.user_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import date
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
from byceps.services.authz import authz_service
from byceps.services.authz.models import RoleID

from . import user_domain_service, user_log_service, user_service
from .dbmodels.detail import DbUserDetail
from .dbmodels.user import DbUser
from .models.log import UserLogEntry
from .models.user import User, UserID


def initialize_account(
    user: User,
    *,
    initiator: User | None = None,
    assign_roles: bool = True,
) -> None:
    """Initialize the user account.

    This is meant to happen only once at most, and can not be undone.
    """
    result = user_domain_service.initialize_account(user, initiator=initiator)

    if result.is_err():
        raise ValueError('Account is already initialized.')

    log_entry = result.unwrap()

    _persist_account_initialization(user.id, log_entry)

    if assign_roles:
        _assign_roles(user, initiator=initiator)


def _persist_account_initialization(
    user_id: UserID, log_entry: UserLogEntry
) -> None:
    db_user = _get_db_user(user_id)

    db_user.initialized = True

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def _assign_roles(user: User, *, initiator: User | None = None) -> None:
    board_user_role_name = 'board_user'
    board_user_role = authz_service.find_role(RoleID(board_user_role_name))
    if board_user_role is None:
        warn(
            f'Role "{board_user_role_name}" not found; '
            f'not assigning it to user "{user.id}".',
            stacklevel=2,
        )
        return

    authz_service.assign_role_to_user(
        board_user_role.id, user, initiator=initiator
    )


def suspend_account(
    user: User, initiator: User, reason: str
) -> UserAccountSuspendedEvent:
    """Suspend the user account."""
    event, log_entry = user_domain_service.suspend_account(
        user, initiator, reason
    )

    _persist_account_suspension(event, log_entry)

    return event


def _persist_account_suspension(
    event: UserAccountSuspendedEvent, log_entry: UserLogEntry
) -> None:
    db_user = _get_db_user(event.user_id)

    db_user.suspended = True

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def unsuspend_account(
    user: User, initiator: User, reason: str
) -> UserAccountUnsuspendedEvent:
    """Unsuspend the user account."""
    event, log_entry = user_domain_service.unsuspend_account(
        user, initiator, reason
    )

    _persist_account_unsuspension(event, log_entry)

    return event


def _persist_account_unsuspension(
    event: UserAccountUnsuspendedEvent, log_entry: UserLogEntry
) -> None:
    db_user = _get_db_user(event.user_id)

    db_user.suspended = False

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def change_screen_name(
    user: User,
    new_screen_name: str,
    initiator: User,
    *,
    reason: str | None = None,
) -> UserScreenNameChangedEvent:
    """Change the user's screen name."""
    event, log_entry = user_domain_service.change_screen_name(
        user, new_screen_name, initiator, reason=reason
    )

    _persist_screen_name_change(event, log_entry)

    return event


def _persist_screen_name_change(
    event: UserScreenNameChangedEvent, log_entry: UserLogEntry
) -> None:
    db_user = _get_db_user(event.user_id)

    db_user.screen_name = event.new_screen_name

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def change_email_address(
    user: User,
    new_email_address: str | None,
    verified: bool,
    initiator: User,
    *,
    reason: str | None = None,
) -> UserEmailAddressChangedEvent:
    """Change the user's e-mail address."""
    db_user = _get_db_user(user.id)
    old_email_address = db_user.email_address

    event, log_entry = user_domain_service.change_email_address(
        user,
        old_email_address,
        new_email_address,
        verified,
        initiator,
        reason=reason,
    )

    _persist_email_address_change(event, new_email_address, verified, log_entry)

    return event


def _persist_email_address_change(
    event: UserEmailAddressChangedEvent,
    new_email_address: str | None,
    verified: bool,
    log_entry: UserLogEntry,
) -> None:
    db_user = _get_db_user(event.user_id)

    db_user.email_address = new_email_address
    db_user.email_address_verified = verified

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def update_locale(user_id: UserID, locale: Locale | None) -> None:
    """Change the user's locale."""
    db_user = _get_db_user(user_id)

    db_user.locale = locale.language if (locale is not None) else None
    db.session.commit()


def update_user_details(
    user_id: UserID,
    new_first_name: str | None,
    new_last_name: str | None,
    new_date_of_birth: date | None,
    new_country: str | None,
    new_zip_code: str | None,
    new_city: str | None,
    new_street: str | None,
    new_phone_number: str | None,
    initiator: User,
) -> UserDetailsUpdatedEvent:
    """Update the user's details."""
    db_detail = _get_db_user_detail(user_id)

    old_first_name = db_detail.first_name
    old_last_name = db_detail.last_name
    old_date_of_birth = db_detail.date_of_birth
    old_country = db_detail.country
    old_zip_code = db_detail.zip_code
    old_city = db_detail.city
    old_street = db_detail.street
    old_phone_number = db_detail.phone_number

    user = user_service.get_user(user_id)
    event, log_entry = user_domain_service.update_details(
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
        initiator,
    )

    _persist_details_update(
        event,
        log_entry,
        db_detail,
        new_first_name,
        new_last_name,
        new_date_of_birth,
        new_country,
        new_zip_code,
        new_city,
        new_street,
        new_phone_number,
    )

    return event


def _persist_details_update(
    event: UserDetailsUpdatedEvent,
    log_entry: UserLogEntry,
    db_detail: DbUserDetail,
    new_first_name: str | None,
    new_last_name: str | None,
    new_date_of_birth: date | None,
    new_country: str | None,
    new_zip_code: str | None,
    new_city: str | None,
    new_street: str | None,
    new_phone_number: str | None,
) -> None:
    db_detail.first_name = new_first_name
    db_detail.last_name = new_last_name
    db_detail.date_of_birth = new_date_of_birth
    db_detail.country = new_country
    db_detail.zip_code = new_zip_code
    db_detail.city = new_city
    db_detail.street = new_street
    db_detail.phone_number = new_phone_number

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def set_user_detail_extra(user_id: UserID, key: str, value: str) -> None:
    """Set a value for a key in the user's detail extras map."""
    detail = _get_db_user_detail(user_id)

    if detail.extras is None:
        detail.extras = {}

    detail.extras[key] = value

    db.session.commit()


def remove_user_detail_extra(user_id: UserID, key: str) -> None:
    """Remove the entry with that key from the user's detail extras map."""
    detail = _get_db_user_detail(user_id)

    if (detail.extras is None) or (key not in detail.extras):
        return

    del detail.extras[key]
    db.session.commit()


def _get_db_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    return user_service.get_db_user(user_id)


def _get_db_user_detail(user_id: UserID) -> DbUserDetail:
    """Return the user's details, or raise an exception."""
    detail = db.session.scalars(
        select(DbUserDetail).filter_by(user_id=user_id)
    ).one_or_none()

    if detail is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return detail
