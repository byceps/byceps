"""
byceps.services.user.creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional, Tuple

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
from ..verification_token import service as verification_token_service

from . import email_address_confirmation_service
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
    terms_consent: Optional[Consent] = None,
    privacy_policy_consent: Optional[Consent] = None,
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

    # consent to terms of service
    if terms_consent:
        terms_consent = consent_service.build_consent(
            user.id, terms_consent.subject_id, terms_consent.expressed_at
        )
        db.session.add(terms_consent)

    # consent to privacy policy
    if privacy_policy_consent:
        privacy_policy_consent = consent_service.build_consent(
            user.id,
            privacy_policy_consent.subject_id,
            privacy_policy_consent.expressed_at,
        )
        db.session.add(privacy_policy_consent)

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
    email_address: str,
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
    screen_name: str,
    email_address: str,
    *,
    first_names: Optional[str] = None,
    last_name: Optional[str] = None,
    creator_id: Optional[UserID] = None,
) -> Tuple[User, UserAccountCreated]:
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
    if creator_id is not None:
        event_data['initiator_id'] = str(creator_id)
    event_service.create_event(
        'user-created', user.id, event_data, occurred_at=created_at
    )

    user_dto = user_service._db_entity_to_user_dto(user)

    event = UserAccountCreated(user_id=user.id, initiator_id=creator_id)

    return user_dto, event


def build_user(
    created_at: datetime, screen_name: str, email_address: str
) -> DbUser:
    normalized_screen_name = _normalize_screen_name(screen_name)
    normalized_email_address = _normalize_email_address(email_address)

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

    verification_token = verification_token_service.create_for_email_address_confirmation(
        user.id
    )

    email_address_confirmation_service.send_email_address_confirmation_email(
        normalized_email_address, user.screen_name, verification_token, site_id
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
