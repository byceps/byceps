"""
byceps.services.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date
from typing import Dict, Iterator, Optional, Set

from flask import url_for

from ...database import db
from ...typing import BrandID, UserID

from ..email import service as email_service
from ..user_avatar.models import Avatar, AvatarSelection
from ..verification_token.models import Token

from . import event_service
from .models.user import AnonymousUser, User as DbUser
from .transfer.models import User


def find_active_user(user_id: UserID) -> Optional[DbUser]:
    """Return the user with that ID if the account is "active", or
    `None` if:
    - the ID is unknown.
    - the account has not been activated, yet.
    - the account is currently suspended.
    - the account is marked as deleted.
    """
    return DbUser.query \
        .filter_by(enabled=True) \
        .filter_by(suspended=False) \
        .filter_by(deleted=False) \
        .filter_by(id=user_id) \
        .one_or_none()


def find_user(user_id: UserID) -> Optional[DbUser]:
    """Return the user with that ID, or `None` if not found."""
    return DbUser.query.get(user_id)


def find_users(user_ids: Set[UserID], *, include_avatars=False) -> Set[User]:
    """Return the users with those IDs.

    Their respective avatars' URLs are included, if requested.
    """
    if not user_ids:
        return set()

    query = db.session \
        .query(
            DbUser.id,
            DbUser.screen_name,
            DbUser.suspended,
            DbUser.deleted,
            Avatar if include_avatars else db.null(),
        )

    if include_avatars:
        query = query \
            .outerjoin(AvatarSelection) \
            .outerjoin(Avatar)

    rows = query \
        .filter(DbUser.id.in_(frozenset(user_ids))) \
        .all()

    def to_dtos() -> Iterator[User]:
        for user_id, screen_name, suspended, deleted, avatar in rows:
            avatar_url = avatar.url if avatar else None
            is_orga = False  # Information is not available here by design.

            yield User(
                user_id,
                screen_name,
                suspended,
                deleted,
                avatar_url,
                is_orga,
            )

    return set(to_dtos())


def find_user_by_screen_name(screen_name: str) -> Optional[DbUser]:
    """Return the user with that screen name, or `None` if not found."""
    return DbUser.query \
        .filter_by(screen_name=screen_name) \
        .one_or_none()


def get_anonymous_user() -> AnonymousUser:
    """Return the anonymous user."""
    return AnonymousUser()


def index_users_by_id(users: Set[User]) -> Dict[UserID, User]:
    """Map the users' IDs to the corresponding user objects."""
    return {user.id: user for user in users}


def is_screen_name_already_assigned(screen_name: str) -> bool:
    """Return `True` if a user with that screen name exists."""
    return _do_users_matching_filter_exist(DbUser.screen_name, screen_name)


def is_email_address_already_assigned(email_address: str) -> bool:
    """Return `True` if a user with that email address exists."""
    return _do_users_matching_filter_exist(DbUser.email_address, email_address)


def _do_users_matching_filter_exist(model_attribute: str, search_value: str
                                   ) -> bool:
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    user_count = DbUser.query \
        .filter(db.func.lower(model_attribute) == search_value.lower()) \
        .count()
    return user_count > 0


def send_email_address_confirmation_email(user: DbUser,
                                          verification_token: Token,
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


def update_user_details(user: DbUser, first_names: str, last_name: str,
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


def suspend_account(user_id: UserID, initiator_id: UserID, reason: str) -> None:
    """Suspend the user account."""
    user = _get_user(user_id)

    user.suspended = True

    event = event_service._build_event('user-suspended', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()


def unsuspend_account(user_id: UserID, initiator_id: UserID, reason: str
                     ) -> None:
    """Unsuspend the user account."""
    user = _get_user(user_id)

    user.suspended = False

    event = event_service._build_event('user-unsuspended', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()


def delete_account(user_id: UserID, initiator_id: UserID, reason: str) -> None:
    """Delete the user account."""
    user = _get_user(user_id)

    user.deleted = True
    _anonymize_account(user)

    event = event_service._build_event('user-deleted', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()


def _anonymize_account(user: DbUser) -> None:
    """Remove or replace user details of the account."""
    user.screen_name = 'deleted-{}'.format(user.id.hex)
    user.email_address = '{}@user.invalid'.format(user.id.hex)
    user.legacy_id = None

    # Remove details.
    user.detail.first_names = None
    user.detail.last_name = None
    user.detail.date_of_birth = None
    user.detail.country = None
    user.detail.zip_code = None
    user.detail.city = None
    user.detail.street = None
    user.detail.phone_number = None

    # Remove avatar association.
    if user.avatar_selection is not None:
        db.session.delete(user.avatar_selection)


def _get_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    user = find_user(user_id)

    if user is None:
        raise ValueError("Unknown user ID '{}'.".format(user_id))

    return user
