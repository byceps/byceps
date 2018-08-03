"""
byceps.services.user.creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import current_app

from ...database import db
from ...typing import BrandID

from ..authentication.password import service as password_service
from ..authorization.models import RoleID
from ..authorization import service as authorization_service
from ..newsletter import command_service as newsletter_command_service
from ..terms.models.version import VersionID as TermsVersionID
from ..terms import service as terms_service
from ..verification_token import service as verification_token_service

from . import event_service
from .models.detail import UserDetail
from .models.user import User
from . import service as user_service


class UserCreationFailed(Exception):
    pass


def create_user(screen_name: str, email_address: str, password: str,
                first_names: str, last_name: str, brand_id: BrandID,
                terms_version_id: TermsVersionID,
                terms_consent_expressed_at: datetime,
                privacy_policy_consent_expressed_at: datetime,
                subscribe_to_newsletter: bool,
                newsletter_subscription_state_expressed_at: datetime) -> User:
    """Create a user account and related records."""
    # user with details
    user = build_user(screen_name, email_address)
    user.detail.first_names = first_names
    user.detail.last_name = last_name
    db.session.add(user)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error('User creation failed: %s', e)
        db.session.rollback()
        raise UserCreationFailed()

    # password
    password_service.create_password_hash(user.id, password)

    # roles
    board_user_role = authorization_service.find_role(RoleID('board_user'))
    authorization_service.assign_role_to_user(user.id, board_user_role.id)

    # consent to terms of service (required)
    terms_consent = terms_service.build_consent_on_account_creation(
        user.id, terms_version_id, terms_consent_expressed_at)
    db.session.add(terms_consent)

    # consent to privacy policy (required)
    event = event_service._build_event('privacy-policy-accepted', user.id, {
        'initiator_id': str(user.id),
    }, occurred_at=privacy_policy_consent_expressed_at)
    db.session.add(event)

    db.session.commit()

    # newsletter subscription (optional)
    if subscribe_to_newsletter:
        newsletter_command_service.subscribe(user.id, brand_id,
            newsletter_subscription_state_expressed_at)

    # verification_token for email address confirmation
    verification_token = verification_token_service \
        .build_for_email_address_confirmation(user.id)
    db.session.add(verification_token)
    db.session.commit()

    user_service.send_email_address_confirmation_email(
        user, verification_token, brand_id)

    return user


def build_user(screen_name: str, email_address: str) -> User:
    normalized_screen_name = _normalize_screen_name(screen_name)
    normalized_email_address = _normalize_email_address(email_address)

    user = User(normalized_screen_name, normalized_email_address)

    detail = UserDetail(user=user)

    return user


def _normalize_screen_name(screen_name: str) -> str:
    """Normalize the screen name, or raise an exception if invalid."""
    normalized = screen_name.strip()

    if not normalized or (' ' in normalized) or ('@' in normalized):
        raise ValueError('Invalid screen name: \'{}\''.format(screen_name))

    return normalized


def _normalize_email_address(email_address: str) -> str:
    """Normalize the e-mail address, or raise an exception if invalid."""
    normalized = email_address.strip()

    if not normalized or (' ' in normalized) or ('@' not in normalized):
        raise ValueError('Invalid email address: \'{}\''.format(email_address))

    return normalized
