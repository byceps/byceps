"""
byceps.services.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date, datetime, timedelta
from typing import Dict, Iterator, Optional, Set

from flask import url_for

from ...database import db
from ...typing import BrandID, UserID

from ..email import service as email_service
from ..user_avatar.models import Avatar, AvatarSelection
from ..verification_token.models import Token

from .models.user import AnonymousUser, User, UserTuple
from . import event_service


def count_users() -> int:
    """Return the number of users."""
    return User.query \
        .count()


def count_users_created_since(delta: timedelta) -> int:
    """Return the number of user accounts created since `delta` ago."""
    filter_starts_at = datetime.now() - delta

    return User.query \
        .filter(User.created_at >= filter_starts_at) \
        .count()


def count_enabled_users() -> int:
    """Return the number of enabled user accounts."""
    return User.query \
        .filter_by(enabled=True) \
        .count()


def count_disabled_users() -> int:
    """Return the number of disabled user accounts."""
    return User.query \
        .filter_by(enabled=False) \
        .count()


def find_user(user_id: UserID) -> Optional[User]:
    """Return the user with that ID, or `None` if not found."""
    return User.query.get(user_id)


def find_users(user_ids: Set[UserID]) -> Set[UserTuple]:
    """Return the users and their current avatars' URLs with those IDs."""
    if not user_ids:
        return set()

    rows = db.session \
        .query(User.id, User.screen_name, User.deleted, Avatar) \
        .outerjoin(AvatarSelection) \
        .outerjoin(Avatar) \
        .filter(User.id.in_(frozenset(user_ids))) \
        .all()

    def to_tuples() -> Iterator[UserTuple]:
        for user_id, screen_name, is_deleted, avatar in rows:
            avatar_url = avatar.url if avatar else None
            is_orga = False  # Information is not available here by design.

            yield UserTuple(
                user_id,
                screen_name,
                is_deleted,
                avatar_url,
                is_orga
            )

    return set(to_tuples())


def find_user_by_screen_name(screen_name: str) -> Optional[User]:
    """Return the user with that screen name, or `None` if not found."""
    return User.query \
        .filter_by(screen_name=screen_name) \
        .one_or_none()


def get_anonymous_user() -> AnonymousUser:
    """Return the anonymous user."""
    return AnonymousUser()


def index_users_by_id(users: Set[UserTuple]) -> Dict[UserID, UserTuple]:
    """Map the users' IDs to the corresponding user objects."""
    return {user.id: user for user in users}


def is_screen_name_already_assigned(screen_name: str) -> bool:
    """Return `True` if a user with that screen name exists."""
    return _do_users_matching_filter_exist(User.screen_name, screen_name)


def is_email_address_already_assigned(email_address: str) -> bool:
    """Return `True` if a user with that email address exists."""
    return _do_users_matching_filter_exist(User.email_address, email_address)


def _do_users_matching_filter_exist(model_attribute: str, search_value: str) -> bool:
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    user_count = User.query \
        .filter(db.func.lower(model_attribute) == search_value.lower()) \
        .count()
    return user_count > 0


def send_email_address_confirmation_email(user: User, verification_token: Token,
                                          brand_id: BrandID) -> None:
    sender_address = email_service.get_sender_address_for_brand(brand_id)

    confirmation_url = url_for('.confirm_email_address',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, bitte bestätige deine E-Mail-Adresse'.format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'bitte bestätige deine E-Mail-Adresse indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    email_service.enqueue_email(sender_address, recipients, subject, body)


def confirm_email_address(verification_token: Token) -> None:
    """Confirm the email address of the user assigned with that
    verification token.
    """
    user = verification_token.user

    user.email_address_verified = True
    user.enabled = True
    db.session.delete(verification_token)
    db.session.commit()


def update_user_details(user: User, first_names: str, last_name: str,
                        date_of_birth: date, country: str, zip_code, city: str,
                        street: str, phone_number: str) -> None:
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


def enable_user(user_id: UserID, initiator_id: UserID) -> None:
    """Enable the user account."""
    user = _get_user(user_id)

    user.enabled = True

    event = event_service._build_event('user-enabled', user.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def disable_user(user_id: UserID, initiator_id: UserID) -> None:
    """Disable the user account."""
    user = _get_user(user_id)

    user.enabled = False

    event = event_service._build_event('user-disabled', user.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def _get_user(user_id: UserID) -> User:
    """Return the user with that ID, or raise an exception."""
    user = find_user(user_id)

    if user is None:
        raise ValueError("Unknown user ID '{}'.".format(user_id))

    return user
