"""
byceps.services.user.user_creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from flask import current_app

from byceps.database import db
from byceps.events.user import UserAccountCreatedEvent
from byceps.services.authentication.password import authn_password_service
from byceps.services.site.models import SiteID
from byceps.util.result import Err, Ok, Result

from . import user_email_address_service, user_log_service, user_service
from .dbmodels.detail import DbUserDetail
from .dbmodels.user import DbUser
from .errors import InvalidEmailAddressError, InvalidScreenNameError
from .models.user import User


def create_user(
    screen_name: str | None,
    email_address: str | None,
    password: str,
    *,
    locale: str | None = None,
    legacy_id: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    country: str | None = None,
    zip_code: str | None = None,
    city: str | None = None,
    street: str | None = None,
    phone_number: str | None = None,
    internal_comment: str | None = None,
    extras: dict[str, Any] | None = None,
    creation_method: str | None = None,
    creator: User | None = None,
    site_id: SiteID | None = None,
    site_title: str | None = None,
    ip_address: str | None = None,
) -> Result[
    tuple[User, UserAccountCreatedEvent],
    InvalidScreenNameError | InvalidEmailAddressError | None,
]:
    """Create a user account and related records."""
    created_at = datetime.utcnow()

    normalized_screen_name: str | None
    if screen_name is not None:
        screen_name_normalization_result = _normalize_screen_name(screen_name)

        if screen_name_normalization_result.is_err():
            return Err(screen_name_normalization_result.unwrap_err())

        normalized_screen_name = screen_name_normalization_result.unwrap()
    else:
        normalized_screen_name = None

    normalized_email_address: str | None
    if email_address is not None:
        email_address_normalization_result = _normalize_email_address(
            email_address
        )

        if email_address_normalization_result.is_err():
            return Err(email_address_normalization_result.unwrap_err())

        normalized_email_address = email_address_normalization_result.unwrap()
    else:
        normalized_email_address = None

    db_user = DbUser(
        created_at,
        normalized_screen_name,
        normalized_email_address,
        locale=locale,
        legacy_id=legacy_id,
    )

    db_detail = DbUserDetail(
        user=db_user,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        country=country,
        zip_code=zip_code,
        city=city,
        street=street,
        phone_number=phone_number,
        internal_comment=internal_comment,
        extras=extras,
    )

    db.session.add(db_user)
    db.session.add(db_detail)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error('User creation failed: %s', e)
        db.session.rollback()
        return Err(None)

    user = user_service._db_entity_to_user(db_user)

    # Create log entry in separate step as user ID is not available earlier.
    _create_user_created_log_entry(
        user,
        db_user.created_at,
        creation_method,
        creator,
        site_id,
        ip_address,
    )

    event = UserAccountCreatedEvent(
        occurred_at=db_user.created_at,
        initiator_id=creator.id if creator else None,
        initiator_screen_name=creator.screen_name if creator else None,
        user_id=user.id,
        user_screen_name=user.screen_name,
        site_id=site_id,
        site_title=site_title,
    )

    # password
    authn_password_service.create_password_hash(user.id, password)

    return Ok((user, event))


def _create_user_created_log_entry(
    user: User,
    created_at: datetime,
    creation_method: str | None,
    creator: User | None,
    site_id: SiteID | None,
    ip_address: str | None,
) -> None:
    log_entry_data = {}

    if creation_method:
        log_entry_data['creation_method'] = creation_method

    if creator is not None:
        log_entry_data['initiator_id'] = str(creator.id)

    if site_id:
        log_entry_data['site_id'] = site_id

    if ip_address:
        log_entry_data['ip_address'] = ip_address

    user_log_service.create_entry(
        'user-created', user.id, log_entry_data, occurred_at=created_at
    )


def request_email_address_confirmation(
    user: User, email_address: str, site_id: SiteID
) -> Result[None, InvalidEmailAddressError]:
    """Send an e-mail to the user to request confirmation of the e-mail
    address.
    """
    normalization_result = _normalize_email_address(email_address)

    if normalization_result.is_err():
        return Err(normalization_result.unwrap_err())

    normalized_email_address = normalization_result.unwrap()

    user_email_address_service.send_email_address_confirmation_email_for_site(
        user, normalized_email_address, site_id
    )

    return Ok(None)


def _normalize_screen_name(
    screen_name: str,
) -> Result[str, InvalidScreenNameError]:
    """Normalize the screen name."""
    normalized = screen_name.strip()

    if not normalized or (' ' in normalized) or ('@' in normalized):
        return Err(InvalidScreenNameError(value=screen_name))

    return Ok(normalized)


def _normalize_email_address(
    email_address: str,
) -> Result[str, InvalidEmailAddressError]:
    """Normalize the e-mail address."""
    normalized = email_address.strip().lower()

    if not normalized or (' ' in normalized) or ('@' not in normalized):
        return Err(InvalidEmailAddressError(value=email_address))

    return Ok(normalized)
