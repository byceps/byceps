# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import current_app, url_for

from ...database import db
from ...services import email as email_service

from ..authentication import service as authentication_service
from ..authorization.models import Role
from ..newsletter import service as newsletter_service
from ..terms import service as terms_service
from ..verification_token import service as verification_token_service

from .models.user import User


def count_users():
    """Return the number of users."""
    return User.query \
        .count()


def count_users_created_since(delta):
    """Return the number of user accounts created since `delta` ago."""
    filter_starts_at = datetime.now() - delta

    return User.query \
        .filter(User.created_at >= filter_starts_at) \
        .count()


def count_enabled_users():
    """Return the number of enabled user accounts."""
    return User.query \
        .filter_by(enabled=True) \
        .count()


def count_disabled_users():
    """Return the number of disabled user accounts."""
    return User.query \
        .filter_by(enabled=False) \
        .count()


def find_user(user_id):
    """Return the user with that id, or `None` if not found."""
    return User.query.get(user_id)


def find_user_by_screen_name(screen_name):
    """Return the user with that screen name, or `None` if not found."""
    return User.query \
        .filter_by(screen_name=screen_name) \
        .one_or_none()


def get_users_with_avatars(user_ids):
    """Return the users (and their avatars) for the IDs."""
    return User.query \
        .filter(User.id.in_(user_ids)) \
        .options(db.joinedload('avatar_selection')) \
        .all()


def is_screen_name_already_assigned(screen_name):
    """Return `True` if a user with that screen name exists."""
    return _do_users_matching_filter_exist(User.screen_name, screen_name)


def is_email_address_already_assigned(email_address):
    """Return `True` if a user with that email address exists."""
    return _do_users_matching_filter_exist(User.email_address, email_address)


def _do_users_matching_filter_exist(model_attribute, search_value):
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    user_count = User.query \
        .filter(db.func.lower(model_attribute) == search_value.lower()) \
        .count()
    return user_count > 0


class UserCreationFailed(Exception):
    pass


def create_user(screen_name, email_address, password, first_names, last_name,
                brand, subscribe_to_newsletter):
    """Create a user account and related records."""
    # user with details
    user = User.create(screen_name, email_address)
    user.detail.first_names = first_names
    user.detail.last_name = last_name
    db.session.add(user)

    # verification_token for email address confirmation
    verification_token = verification_token_service \
        .build_for_email_address_confirmation(user)
    db.session.add(verification_token)

    # consent to terms of service (required)
    terms_version = terms_service.get_current_version(brand)
    terms_consent = terms_service.build_consent_on_account_creation(user,
                                                                    terms_version)
    db.session.add(terms_consent)

    # roles
    board_user_role = Role.query.get('board_user')
    user.roles.add(board_user_role)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error('User creation failed: %s', e)
        db.session.rollback()
        raise UserCreationFailed()

    # password
    authentication_service.create_password_hash(user, password)

    # newsletter subscription (optional)
    _create_newsletter_subscription(user.id, brand.id, subscribe_to_newsletter)

    send_email_address_confirmation_email(user, verification_token)

    return user


def _create_newsletter_subscription(user_id, brand_id, subscribe_to_newsletter):
    if subscribe_to_newsletter:
        newsletter_service.subscribe(user_id, brand_id)
    else:
        newsletter_service.unsubscribe(user_id, brand_id)


def send_email_address_confirmation_email(user, verification_token):
    confirmation_url = url_for('.confirm_email_address',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, bitte bestätige deine E-Mail-Adresse'.format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'bitte bestätige deine E-Mail-Adresse indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    email_service.send(subject=subject, body=body, recipients=recipients)


def confirm_email_address(verification_token):
    """Confirm the email address of the user assigned with that
    verification token.
    """
    user = verification_token.user

    user.enabled = True
    db.session.delete(verification_token)
    db.session.commit()


def update_user_details(user, first_names, last_name, date_of_birth, country,
                        zip_code, city, street, phone_number):
    """Update the user's details."""
    user.detail.first_names = first_names
    user.detail.last_name = last_name
    user.detail.date_of_birth = date_of_birth
    user.detail.country = country
    user.detail.zip_code = zip_code
    user.detail.city = city
    user.detail.street = street
    user.detail.phone_number = phone_number

    db.session.commit()
