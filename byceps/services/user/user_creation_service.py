"""
byceps.services.user.user_creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime
from typing import Any, Optional

from flask import current_app

from ...database import db
from ...events.user import UserAccountCreated
from ...typing import UserID

from ..authentication.password import authn_password_service
from ..site.models import SiteID

from . import user_email_address_service, user_log_service, user_service
from .dbmodels.detail import DbUserDetail
from .dbmodels.user import DbUser
from .models.user import User


class UserCreationFailed(Exception):
    pass


def create_user(
    screen_name: Optional[str],
    email_address: Optional[str],
    password: str,
    *,
    locale: Optional[str] = None,
    legacy_id: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    country: Optional[str] = None,
    zip_code: Optional[str] = None,
    city: Optional[str] = None,
    street: Optional[str] = None,
    phone_number: Optional[str] = None,
    internal_comment: Optional[str] = None,
    extras: Optional[dict[str, Any]] = None,
    creation_method: Optional[str] = None,
    creator_id: Optional[UserID] = None,
    site_id: Optional[SiteID] = None,
    ip_address: Optional[str] = None,
) -> tuple[User, UserAccountCreated]:
    """Create a user account and related records."""
    creator: Optional[User]
    if creator_id is not None:
        creator = user_service.get_user(creator_id)
    else:
        creator = None

    created_at = datetime.utcnow()

    normalized_screen_name: Optional[str]
    if screen_name is not None:
        normalized_screen_name = _normalize_screen_name(screen_name)
    else:
        normalized_screen_name = None

    normalized_email_address: Optional[str]
    if email_address is not None:
        normalized_email_address = _normalize_email_address(email_address)
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
        raise UserCreationFailed()

    user = user_service._db_entity_to_user(db_user)

    # Create log entry in separate step as user ID is not available earlier.
    _create_user_created_log_entry(
        user.id,
        db_user.created_at,
        creation_method,
        creator,
        site_id,
        ip_address,
    )

    event = UserAccountCreated(
        occurred_at=db_user.created_at,
        initiator_id=creator.id if creator else None,
        initiator_screen_name=creator.screen_name if creator else None,
        user_id=user.id,
        user_screen_name=user.screen_name,
        site_id=site_id,
    )

    # password
    authn_password_service.create_password_hash(user.id, password)

    return user, event


def _create_user_created_log_entry(
    user_id: UserID,
    created_at: datetime,
    creation_method: Optional[str],
    creator: Optional[User],
    site_id: Optional[SiteID],
    ip_address: Optional[str],
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
        'user-created', user_id, log_entry_data, occurred_at=created_at
    )


def request_email_address_confirmation(
    user: User, email_address: str, site_id: SiteID
) -> None:
    """Send an e-mail to the user to request confirmation of the e-mail
    address.
    """
    normalized_email_address = _normalize_email_address(email_address)

    user_email_address_service.send_email_address_confirmation_email_for_site(
        user, normalized_email_address, site_id
    )


def _normalize_screen_name(screen_name: str) -> str:
    """Normalize the screen name, or raise an exception if invalid."""
    normalized = screen_name.strip()

    if not normalized or (' ' in normalized) or ('@' in normalized):
        raise ValueError(f"Invalid screen name: '{screen_name}'")

    return normalized


def _normalize_email_address(email_address: str) -> str:
    """Normalize the e-mail address, or raise an exception if invalid."""
    normalized = email_address.strip().lower()

    if not normalized or (' ' in normalized) or ('@' not in normalized):
        raise ValueError(f"Invalid email address: '{email_address}'")

    return normalized
