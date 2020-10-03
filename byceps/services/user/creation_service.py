"""
byceps.services.user.creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional, Set, Tuple

from flask import current_app

from ...database import db
from ...events.user import UserAccountCreated
from ...typing import UserID

from ..authentication.password import service as password_service
from ..consent import consent_service
from ..consent.transfer.models import Consent
from ..newsletter import command_service as newsletter_command_service
from ..newsletter.transfer.models import Subscription as NewsletterSubscription
from ..site.transfer.models import SiteID

from . import email_address_verification_service
from . import event_service
from .models.detail import UserDetail as DbUserDetail
from .models.user import User as DbUser
from . import service as user_service
from .transfer.models import User


class UserCreationFailed(Exception):
    pass


def create_user(
    screen_name: str,
    email_address: str,
    password: str,
    first_names: Optional[str],
    last_name: Optional[str],
    site_id: SiteID,
    *,
    consents: Optional[Set[Consent]] = None,
    newsletter_subscription: Optional[NewsletterSubscription] = None,
) -> Tuple[User, UserAccountCreated]:
    """Create a user account and related records."""
    # user with details, password, and roles
    user, event = create_basic_user(
        screen_name,
        email_address,
        password,
        first_names=first_names,
        last_name=last_name,
    )

    # consents
    if consents:
        for consent in consents:
            # Insert missing user ID.
            consent = consent_service.build_consent(
                user.id,
                consent.subject_id,
                consent.expressed_at,
            )
            db.session.add(consent)

    db.session.commit()

    # newsletter subscription (optional)
    if newsletter_subscription:
        newsletter_command_service.subscribe(
            user.id,
            newsletter_subscription.list_id,
            newsletter_subscription.expressed_at,
        )

    request_email_address_confirmation(user, email_address, site_id)

    return user, event


def create_basic_user(
    screen_name: str,
    email_address: Optional[str],
    password: str,
    *,
    first_names: Optional[str] = None,
    last_name: Optional[str] = None,
    creator_id: Optional[UserID] = None,
) -> Tuple[User, UserAccountCreated]:
    # user with details
    user, event = _create_user(
        screen_name,
        email_address,
        first_names=first_names,
        last_name=last_name,
        creator_id=creator_id,
    )

    # password
    password_service.create_password_hash(user.id, password)

    return user, event


def _create_user(
    screen_name: Optional[str],
    email_address: Optional[str],
    *,
    first_names: Optional[str] = None,
    last_name: Optional[str] = None,
    creator_id: Optional[UserID] = None,
) -> Tuple[User, UserAccountCreated]:
    if creator_id is not None:
        creator = user_service.get_user(creator_id)
    else:
        creator = None

    created_at = datetime.utcnow()

    user = build_user(created_at, screen_name, email_address)

    user.detail.first_names = first_names
    user.detail.last_name = last_name

    db.session.add(user)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error('User creation failed: %s', e)
        db.session.rollback()
        raise UserCreationFailed()

    # Create event in separate step as user ID is not available earlier.
    event_data = {}
    if creator is not None:
        event_data['initiator_id'] = str(creator.id)
    event_service.create_event(
        'user-created', user.id, event_data, occurred_at=created_at
    )

    user_dto = user_service._db_entity_to_user(user)

    event = UserAccountCreated(
        occurred_at=user.created_at,
        initiator_id=creator.id if creator else None,
        initiator_screen_name=creator.screen_name if creator else None,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    return user_dto, event


def build_user(
    created_at: datetime,
    screen_name: Optional[str],
    email_address: Optional[str],
) -> DbUser:
    if screen_name is not None:
        normalized_screen_name = _normalize_screen_name(screen_name)
    else:
        normalized_screen_name = None

    if email_address is not None:
        normalized_email_address = _normalize_email_address(email_address)
    else:
        normalized_email_address = None

    user = DbUser(created_at, normalized_screen_name, normalized_email_address)

    detail = DbUserDetail(user=user)

    return user


def request_email_address_confirmation(
    user: User, email_address: str, site_id: SiteID
) -> None:
    """Send an e-mail to the user to request confirmation of the e-mail
    address.
    """
    normalized_email_address = _normalize_email_address(email_address)

    email_address_verification_service.send_email_address_confirmation_email(
        normalized_email_address, user.screen_name, user.id, site_id
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
