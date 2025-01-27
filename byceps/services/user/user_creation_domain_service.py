"""
byceps.services.user.user_creation_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.events.base import EventSite, EventUser
from byceps.events.user import UserAccountCreatedEvent
from byceps.services.site.models import Site
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid4, generate_uuid7

from .errors import (
    AccountAlreadyInitializedError,
    InvalidEmailAddressError,
    InvalidScreenNameError,
)
from .models.log import UserLogEntry
from .models.user import User, UserID


def create_account(
    screen_name: str | None,
    email_address: str | None,
    password: str,
    *,
    locale: str | None = None,
    creation_method: str | None = None,
    site: Site | None = None,
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

    event = _build_account_created_event(occurred_at, initiator, user, site)

    log_entry = _build_account_created_log_entry(
        occurred_at, initiator, user, creation_method, site, ip_address
    )

    return Ok((user, normalized_email_address, event, log_entry))


def _build_account_created_event(
    occurred_at: datetime,
    initiator: User | None,
    user: User,
    site: Site | None = None,
) -> UserAccountCreatedEvent:
    return UserAccountCreatedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator) if initiator else None,
        user=EventUser.from_user(user),
        site=EventSite.from_site(site) if site else None,
    )


def _build_account_created_log_entry(
    occurred_at: datetime,
    initiator: User | None,
    user: User,
    creation_method: str | None,
    site: Site | None,
    ip_address: str | None,
) -> UserLogEntry:
    data = {}

    if initiator is not None:
        data['initiator_id'] = str(initiator.id)

    if creation_method:
        data['creation_method'] = creation_method

    if site:
        data['site_id'] = site.id

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
    normalized = email_address.strip()

    if not normalized or (' ' in normalized) or ('@' not in normalized):
        return Err(InvalidEmailAddressError(value=email_address))

    return Ok(normalized)
