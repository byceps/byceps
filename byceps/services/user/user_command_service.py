"""
byceps.services.user.user_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date
from warnings import warn

from babel import Locale

from byceps.services.authn.password import authn_password_service
from byceps.services.authn.session import authn_session_service
from byceps.services.authz import authz_service
from byceps.services.authz.models import RoleID
from byceps.services.newsletter import newsletter_command_service
from byceps.services.user.log import user_log_service
from byceps.services.verification_token import verification_token_service
from byceps.util.result import Err, Ok, Result

from . import (
    user_creation_domain_service,
    user_domain_service,
    user_email_address_domain_service,
    user_repository,
    user_service,
)
from .errors import NothingChangedError
from .events import (
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserScreenNameChangedEvent,
)
from .models import User, UserID


def initialize_account(
    user: User,
    *,
    initiator: User | None = None,
    assign_roles: bool = True,
) -> None:
    """Initialize the user account.

    This is meant to happen only once at most, and can not be undone.
    """
    result = user_creation_domain_service.initialize_account(
        user, initiator=initiator
    )

    if result.is_err():
        raise ValueError('Account is already initialized.')

    log_entry = result.unwrap()

    initialized = True
    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.update_initialized_flag(user.id, initialized, db_log_entry)

    if assign_roles:
        _assign_roles(user, initiator=initiator)


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

    suspended = True
    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.update_suspended_flag(
        event.user.id, suspended, db_log_entry
    )

    return event


def unsuspend_account(
    user: User, initiator: User, reason: str
) -> UserAccountUnsuspendedEvent:
    """Unsuspend the user account."""
    event, log_entry = user_domain_service.unsuspend_account(
        user, initiator, reason
    )

    suspended = False
    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.update_suspended_flag(
        event.user.id, suspended, db_log_entry
    )

    return event


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

    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.update_screen_name(
        event.user.id, event.new_screen_name, db_log_entry
    )

    return event


def change_email_address(
    user: User,
    new_email_address: str | None,
    verified: bool,
    initiator: User,
    *,
    reason: str | None = None,
) -> UserEmailAddressChangedEvent:
    """Change the user's e-mail address."""
    db_user = user_repository.get_db_user(user.id)
    old_email_address = db_user.email_address

    event, log_entry = user_email_address_domain_service.change_email_address(
        user,
        old_email_address,
        new_email_address,
        verified,
        initiator,
        reason=reason,
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.update_email_address(
        event.user.id, new_email_address, verified, db_log_entry
    )

    return event


def update_locale(user_id: UserID, locale: Locale | None) -> None:
    """Change the user's locale."""
    user_repository.update_locale(user_id, locale)


def update_user_details(
    user_id: UserID,
    new_first_name: str | None,
    new_last_name: str | None,
    new_date_of_birth: date | None,
    new_country: str | None,
    new_postal_code: str | None,
    new_city: str | None,
    new_street: str | None,
    new_phone_number: str | None,
    initiator: User,
) -> Result[UserDetailsUpdatedEvent, NothingChangedError]:
    """Update the user's details."""
    db_detail = user_repository.get_detail(user_id)

    old_first_name = db_detail.first_name
    old_last_name = db_detail.last_name
    old_date_of_birth = db_detail.date_of_birth
    old_country = db_detail.country
    old_postal_code = db_detail.postal_code
    old_city = db_detail.city
    old_street = db_detail.street
    old_phone_number = db_detail.phone_number

    user = user_service.get_user(user_id)
    domain_update_result = user_domain_service.update_details(
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
        initiator,
    )
    if domain_update_result.is_err():
        return Err(domain_update_result.unwrap_err())

    event, log_entry = domain_update_result.unwrap()

    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.update_details(
        user.id,
        new_first_name,
        new_last_name,
        new_date_of_birth,
        new_country,
        new_postal_code,
        new_city,
        new_street,
        new_phone_number,
        db_log_entry,
    )

    return Ok(event)


def set_user_detail_extra(user_id: UserID, key: str, value: str) -> None:
    """Set a value for a key in the user's detail extras map."""
    user_repository.set_detail_extra(user_id, key, value)


def remove_user_detail_extra(user_id: UserID, key: str) -> None:
    """Remove the entry with that key from the user's detail extras map."""
    user_repository.remove_detail_extra(user_id, key)


def delete_account(
    user: User, initiator: User, reason: str
) -> UserAccountDeletedEvent:
    """Delete the user account."""
    event, log_entry = user_domain_service.delete_account(
        user, initiator, reason
    )

    authz_service.deassign_all_roles_from_user(
        user, initiator=initiator, commit=False
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.delete_user(user, initiator, db_log_entry)

    authn_session_service.delete_session_tokens_for_user(user.id)
    authn_password_service.delete_password_hash(user.id)
    verification_token_service.delete_tokens_for_user(user.id)
    newsletter_command_service.unsubscribe_user_from_lists(
        user, log_entry.occurred_at, initiator
    )

    return event
