"""
byceps.services.user.creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any, Optional

from flask import current_app

from ...database import db
from ...events.user import UserAccountCreated
from ...typing import UserID

from ..authentication.password import service as password_service
from ..site.transfer.models import SiteID

from . import email_address_verification_service
from . import event_service
from .dbmodels.detail import UserDetail as DbUserDetail
from .dbmodels.user import User as DbUser
from . import service as user_service
from .transfer.models import User


class UserCreationFailed(Exception):
    pass


def create_user(
    screen_name: Optional[str],
    email_address: Optional[str],
    password: str,
    *,
    legacy_id: Optional[str] = None,
    first_names: Optional[str] = None,
    last_name: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    country: Optional[str] = None,
    zip_code: Optional[str] = None,
    city: Optional[str] = None,
    street: Optional[str] = None,
    phone_number: Optional[str] = None,
    internal_comment: Optional[str] = None,
    extras: Optional[dict[str, Any]] = None,
    creator_id: Optional[UserID] = None,
    site_id: Optional[SiteID] = None,
) -> tuple[User, UserAccountCreated]:
    """Create a user account and related records."""
    creator: Optional[User]
    if creator_id is not None:
        creator = user_service.get_user(creator_id)
    else:
        creator = None

    created_at = datetime.utcnow()

    db_user = build_db_user(
        created_at, screen_name, email_address, legacy_id=legacy_id
    )

    db_user.detail.first_names = first_names
    db_user.detail.last_name = last_name
    db_user.detail.date_of_birth = date_of_birth
    db_user.detail.country = country
    db_user.detail.zip_code = zip_code
    db_user.detail.city = city
    db_user.detail.street = street
    db_user.detail.phone_number = phone_number
    db_user.detail.internal_comment = internal_comment
    db_user.detail.extras = extras

    db.session.add(db_user)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error('User creation failed: %s', e)
        db.session.rollback()
        raise UserCreationFailed()

    user = user_service._db_entity_to_user(db_user)

    # Create event in separate step as user ID is not available earlier.
    event_data = {}
    if creator is not None:
        event_data['initiator_id'] = str(creator.id)
    if site_id is not None:
        event_data['site_id'] = site_id
    event_service.create_event(
        'user-created', user.id, event_data, occurred_at=created_at
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
    password_service.create_password_hash(user.id, password)

    return user, event


def build_db_user(
    created_at: datetime,
    screen_name: Optional[str],
    email_address: Optional[str],
    *,
    legacy_id: Optional[str] = None,
) -> DbUser:
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

    user = DbUser(
        created_at,
        normalized_screen_name,
        normalized_email_address,
        legacy_id=legacy_id,
    )

    detail = DbUserDetail(user=user)

    return user


def request_email_address_confirmation(
    user: User, email_address: str, site_id: SiteID
) -> None:
    """Send an e-mail to the user to request confirmation of the e-mail
    address.
    """
    normalized_email_address = _normalize_email_address(email_address)
    screen_name = user.screen_name if user.screen_name else 'UnknownUser'

    email_address_verification_service.send_email_address_confirmation_email(
        normalized_email_address, screen_name, user.id, site_id
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
