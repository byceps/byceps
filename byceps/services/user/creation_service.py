"""
byceps.services.user.creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from flask import current_app

from ...database import db
from ...typing import BrandID, UserID

from ..authentication.password import service as password_service
from ..authorization.models import RoleID
from ..authorization import service as authorization_service
from ..newsletter import command_service as newsletter_command_service
from ..terms.models.version import VersionID as TermsVersionID
from ..terms import consent_service as terms_consent_service
from ..verification_token import service as verification_token_service

from . import event_service
from .models.detail import UserDetail as DbUserDetail
from .models.user import User as DbUser
from . import service as user_service
from .transfer.models import User


class UserCreationFailed(Exception):
    pass


def create_user(screen_name: str, email_address: str, password: str,
                first_names: Optional[str], last_name: Optional[str],
                brand_id: BrandID, terms_consent_required: bool,
                terms_version_id: Optional[TermsVersionID],
                terms_consent_expressed_at: Optional[datetime],
                privacy_policy_consent_required: bool,
                privacy_policy_consent_expressed_at: Optional[datetime],
                subscribe_to_newsletter: bool,
                newsletter_subscription_state_expressed_at: datetime) -> User:
    """Create a user account and related records."""
    # user with details
    user = _create_user(screen_name, email_address, first_names, last_name)

    # password
    password_service.create_password_hash(user.id, password)

    # roles
    _assign_roles(user.id)

    # consent to terms of service
    if terms_consent_required:
        terms_consent = terms_consent_service.build_consent_on_account_creation(
            user.id, terms_version_id, terms_consent_expressed_at)
        db.session.add(terms_consent)

    # consent to privacy policy
    if privacy_policy_consent_required:
        event = event_service._build_event('privacy-policy-accepted', user.id, {
            'initiator_id': str(user.id),
        }, occurred_at=privacy_policy_consent_expressed_at)
        db.session.add(event)

    db.session.commit()

    # newsletter subscription (optional)
    if subscribe_to_newsletter:
        newsletter_command_service.subscribe(user.id, brand_id,
            newsletter_subscription_state_expressed_at)

    # e-mail address confirmation
    _request_email_address_verification(user, brand_id)

    return user_service._db_entity_to_user_dto(user)


def build_user(screen_name: str, email_address: str) -> DbUser:
    normalized_screen_name = _normalize_screen_name(screen_name)
    normalized_email_address = _normalize_email_address(email_address)

    user = DbUser(normalized_screen_name, normalized_email_address)

    detail = DbUserDetail(user=user)

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


def _create_user(screen_name: str, email_address: str,
                 first_names: Optional[str], last_name: Optional[str]
                ) -> DbUser:
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

    return user


def _assign_roles(user_id: UserID) -> None:
    board_user_role = authorization_service.find_role(RoleID('board_user'))

    authorization_service.assign_role_to_user(user_id, board_user_role.id)


def _request_email_address_verification(user: DbUser, brand_id: BrandID
                                       ) -> None:
    verification_token = verification_token_service \
        .create_for_email_address_confirmation(user.id)

    user_service.send_email_address_confirmation_email(user.email_address,
        user.screen_name, verification_token, brand_id)
