"""
byceps.services.user.user_creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date
from typing import Any

from babel import Locale
import structlog

from byceps.database import db
from byceps.services.authn.password import authn_password_service
from byceps.services.site.models import Site, SiteID
from byceps.services.user.log import user_log_service
from byceps.util.result import Err, Ok, Result

from . import (
    user_creation_domain_service,
    user_email_address_service,
    user_service,
)
from .dbmodels.detail import DbUserDetail
from .dbmodels.user import DbUser
from .errors import InvalidEmailAddressError, InvalidScreenNameError
from .events import UserAccountCreatedEvent
from .models.user import Password, User


log = structlog.get_logger()


def create_user(
    screen_name: str | None,
    email_address: str | None,
    password: Password,
    *,
    locale: Locale | None = None,
    legacy_id: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    country: str | None = None,
    postal_code: str | None = None,
    city: str | None = None,
    street: str | None = None,
    phone_number: str | None = None,
    internal_comment: str | None = None,
    extras: dict[str, Any] | None = None,
    creation_method: str | None = None,
    creator: User | None = None,
    site: Site | None = None,
    ip_address: str | None = None,
) -> Result[
    tuple[User, UserAccountCreatedEvent],
    InvalidScreenNameError | InvalidEmailAddressError | None,
]:
    """Create a user account and related records."""
    if email_address is not None:
        existing_user_by_email_address = (
            user_service.find_user_by_email_address(email_address)
        )
        if existing_user_by_email_address:
            log.info(
                'User creation failed',
                reason='email address already in database',
            )
            return Err(InvalidEmailAddressError(value=email_address))

    result = user_creation_domain_service.create_account(
        screen_name,
        email_address,
        locale=locale,
        creation_method=creation_method,
        site=site,
        ip_address=ip_address,
        initiator=creator,
    )

    if result.is_err():
        return Err(result.unwrap_err())

    user, normalized_email_address, event, log_entry = result.unwrap()

    db_user = DbUser(
        user.id,
        event.occurred_at,
        user.screen_name,
        normalized_email_address,
        locale=user.locale,
        legacy_id=legacy_id,
    )
    db.session.add(db_user)

    db_detail = DbUserDetail(
        user=db_user,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        country=country,
        postal_code=postal_code,
        city=city,
        street=street,
        phone_number=phone_number,
        internal_comment=internal_comment,
        extras=extras,
    )
    db.session.add(db_detail)

    try:
        db.session.commit()
    except Exception as exc:
        log.error('User creation failed', exc_info=exc)
        db.session.rollback()
        return Err(None)

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)
    db.session.commit()

    user = user_service._db_entity_to_user(db_user)

    # password
    authn_password_service.create_password_hash(user.id, password)

    return Ok((user, event))


def request_email_address_confirmation(
    user: User, email_address: str, site_id: SiteID
) -> Result[None, InvalidEmailAddressError]:
    """Send an e-mail to the user to request confirmation of the e-mail
    address.
    """
    normalization_result = user_creation_domain_service.normalize_email_address(
        email_address
    )

    if normalization_result.is_err():
        return Err(normalization_result.unwrap_err())

    normalized_email_address = normalization_result.unwrap()

    user_email_address_service.send_email_address_confirmation_email_for_site(
        user, normalized_email_address, site_id
    )

    return Ok(None)
