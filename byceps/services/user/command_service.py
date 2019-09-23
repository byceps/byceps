"""
byceps.services.user.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date
from typing import Optional

from ...database import db
from ...typing import UserID

from ..authorization import service as authorization_service

from . import event_service
from .models.detail import UserDetail as DbUserDetail
from .models.user import User as DbUser


def initialize_account(user_id: UserID, initiator_id: UserID) -> None:
    """Initialize the user account.

    This is meant to happen only once at most, and can not be undone.
    """
    user = _get_user(user_id)

    if user.initialized:
        raise ValueError(f'Account is already initialized.')

    user.initialized = True

    event = event_service.build_event('user-initialized', user.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def suspend_account(user_id: UserID, initiator_id: UserID, reason: str) -> None:
    """Suspend the user account."""
    user = _get_user(user_id)

    user.suspended = True

    event = event_service.build_event('user-suspended', user.id, {
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

    event = event_service.build_event('user-unsuspended', user.id, {
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

    event = event_service.build_event('user-deleted', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    # Deassign authorization roles.
    authorization_service.deassign_all_roles_from_user(user.id, initiator_id,
                                                       commit=False)

    db.session.commit()


def change_screen_name(user_id: UserID, new_screen_name: str,
                       initiator_id: UserID, *, reason: Optional[str]=None
                      ) -> None:
    """Change the user's screen name."""
    user = _get_user(user_id)

    old_screen_name = user.screen_name

    user.screen_name = new_screen_name

    event_data = {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'initiator_id': str(initiator_id),
    }
    if reason:
        event_data['reason'] = reason

    event = event_service.build_event('user-screen-name-changed', user.id,
                                      event_data)
    db.session.add(event)

    db.session.commit()


def change_email_address(user_id: UserID, new_email_address: str,
                         initiator_id: UserID, *, reason: Optional[str]=None
                        ) -> None:
    """Change the user's e-mail address."""
    user = _get_user(user_id)

    old_email_address = user.email_address

    user.email_address = new_email_address
    user.email_address_verified = False

    event_data = {
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
        'initiator_id': str(initiator_id),
    }
    if reason:
        event_data['reason'] = reason

    event = event_service.build_event('user-email-address-changed', user.id,
                                      event_data)
    db.session.add(event)

    db.session.commit()


def update_user_details(user_id: UserID, first_names: str, last_name: str,
                        date_of_birth: date, country: str, zip_code, city: str,
                        street: str, phone_number: str) -> None:
    """Update the user's details."""
    detail = _get_user_detail(user_id)

    detail.first_names = first_names
    detail.last_name = last_name
    detail.date_of_birth = date_of_birth
    detail.country = country
    detail.zip_code = zip_code
    detail.city = city
    detail.street = street
    detail.phone_number = phone_number

    db.session.commit()


def set_user_detail_extra(user_id: UserID, key: str, value: str) -> None:
    """Set a value for a key in the user's detail extras map."""
    detail = _get_user_detail(user_id)

    if detail.extras is None:
        detail.extras = {}

    detail.extras[key] = value

    db.session.commit()


def remove_user_detail_extra(user_id: UserID, key: str) -> None:
    """Remove the entry with that key from the user's detail extras map."""
    detail = _get_user_detail(user_id)

    if (detail.extras is None) or (key not in detail.extras):
        return

    del detail.extras[key]
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
    user = DbUser.query.get(user_id)

    if user is None:
        raise ValueError("Unknown user ID '{}'.".format(user_id))

    return user


def _get_user_detail(user_id: UserID) -> DbUserDetail:
    """Return the user's details, or raise an exception."""
    detail = DbUserDetail.query \
        .filter_by(user_id=user_id) \
        .one_or_none()

    if detail is None:
        raise ValueError("Unknown user ID '{}'.".format(user_id))

    return detail
