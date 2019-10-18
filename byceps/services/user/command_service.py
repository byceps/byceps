"""
byceps.services.user.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date
from typing import Optional

from ...database import db
from ...events.user import (
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserScreenNameChanged,
)
from ...typing import UserID

from ..authorization.models import RoleID
from ..authorization import service as authorization_service

from . import event_service
from .models.detail import UserDetail as DbUserDetail
from .models.user import User as DbUser


def initialize_account(
    user_id: UserID, *, initiator_id: Optional[UserID] = None
) -> None:
    """Initialize the user account.

    This is meant to happen only once at most, and can not be undone.
    """
    user = _get_user(user_id)

    if user.initialized:
        raise ValueError(f'Account is already initialized.')

    user.initialized = True

    event_data = {}
    if initiator_id:
        event_data['initiator_id'] = str(initiator_id)
    event = event_service.build_event('user-initialized', user.id, event_data)
    db.session.add(event)

    db.session.commit()

    _assign_roles(user.id, initiator_id=initiator_id)


def _assign_roles(
    user_id: UserID, *, initiator_id: Optional[UserID] = None
) -> None:
    board_user_role = authorization_service.find_role(RoleID('board_user'))

    authorization_service.assign_role_to_user(
        board_user_role.id, user_id, initiator_id=initiator_id
    )


def suspend_account(
    user_id: UserID, initiator_id: UserID, reason: str
) -> UserAccountSuspended:
    """Suspend the user account."""
    user = _get_user(user_id)

    user.suspended = True

    event = event_service.build_event('user-suspended', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()

    return UserAccountSuspended(user_id=user.id, initiator_id=initiator_id)


def unsuspend_account(
    user_id: UserID, initiator_id: UserID, reason: str
) -> UserAccountUnsuspended:
    """Unsuspend the user account."""
    user = _get_user(user_id)

    user.suspended = False

    event = event_service.build_event('user-unsuspended', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()

    return UserAccountUnsuspended(user_id=user.id, initiator_id=initiator_id)


def delete_account(
    user_id: UserID, initiator_id: UserID, reason: str
) -> UserAccountDeleted:
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
    authorization_service.deassign_all_roles_from_user(
        user.id, initiator_id, commit=False
    )

    db.session.commit()

    return UserAccountDeleted(user_id=user.id, initiator_id=initiator_id)


def change_screen_name(
    user_id: UserID,
    new_screen_name: str,
    initiator_id: UserID,
    *,
    reason: Optional[str] = None,
) -> UserScreenNameChanged:
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

    event = event_service.build_event(
        'user-screen-name-changed', user.id, event_data
    )
    db.session.add(event)

    db.session.commit()

    return UserScreenNameChanged(
        user_id=user.id,
        initiator_id=initiator_id,
        old_screen_name=old_screen_name,
        new_screen_name=new_screen_name,
    )


def change_email_address(
    user_id: UserID,
    new_email_address: str,
    initiator_id: UserID,
    *,
    reason: Optional[str] = None,
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

    event = event_service.build_event(
        'user-email-address-changed', user.id, event_data
    )
    db.session.add(event)

    db.session.commit()


def update_user_details(
    user_id: UserID,
    first_names: str,
    last_name: str,
    date_of_birth: date,
    country: str,
    zip_code,
    city: str,
    street: str,
    phone_number: str,
) -> None:
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
    user.screen_name = f'deleted-{user.id.hex}'
    user.email_address = f'{user.id.hex}@user.invalid'
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
        raise ValueError(f"Unknown user ID '{user_id}'")

    return user


def _get_user_detail(user_id: UserID) -> DbUserDetail:
    """Return the user's details, or raise an exception."""
    detail = DbUserDetail.query \
        .filter_by(user_id=user_id) \
        .one_or_none()

    if detail is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return detail
