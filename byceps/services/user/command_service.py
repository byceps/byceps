"""
byceps.services.user.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date
from typing import Any, Optional

from ...database import db
from ...events.user import (
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressChanged,
    UserScreenNameChanged,
)
from ...typing import UserID

from ..authorization.models import RoleID
from ..authorization import service as authorization_service

from . import event_service
from .models.detail import UserDetail as DbUserDetail
from .models.event import UserEventData
from .models.user import User as DbUser
from . import service as user_service


def initialize_account(
    user_id: UserID,
    *,
    initiator_id: Optional[UserID] = None,
    assign_roles: bool = True,
) -> None:
    """Initialize the user account.

    This is meant to happen only once at most, and can not be undone.
    """
    user = _get_user(user_id)

    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    if user.initialized:
        raise ValueError(f'Account is already initialized.')

    user.initialized = True

    event_data = {}
    if initiator:
        event_data['initiator_id'] = str(initiator.id)
    event = event_service.build_event('user-initialized', user.id, event_data)
    db.session.add(event)

    db.session.commit()

    if assign_roles:
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
    initiator = user_service.get_user(initiator_id)

    user.suspended = True

    event = event_service.build_event(
        'user-suspended',
        user.id,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
    )
    db.session.add(event)

    db.session.commit()

    return UserAccountSuspended(
        occurred_at=event.occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def unsuspend_account(
    user_id: UserID, initiator_id: UserID, reason: str
) -> UserAccountUnsuspended:
    """Unsuspend the user account."""
    user = _get_user(user_id)
    initiator = user_service.get_user(initiator_id)

    user.suspended = False

    event = event_service.build_event(
        'user-unsuspended',
        user.id,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
    )
    db.session.add(event)

    db.session.commit()

    return UserAccountUnsuspended(
        occurred_at=event.occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def change_screen_name(
    user_id: UserID,
    new_screen_name: str,
    initiator_id: UserID,
    *,
    reason: Optional[str] = None,
) -> UserScreenNameChanged:
    """Change the user's screen name."""
    user = _get_user(user_id)
    initiator = user_service.get_user(initiator_id)

    old_screen_name = user.screen_name

    user.screen_name = new_screen_name

    event_data = {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'initiator_id': str(initiator.id),
    }
    if reason:
        event_data['reason'] = reason

    event = event_service.build_event(
        'user-screen-name-changed', user.id, event_data
    )
    db.session.add(event)

    db.session.commit()

    return UserScreenNameChanged(
        occurred_at=event.occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        old_screen_name=old_screen_name,
        new_screen_name=new_screen_name,
    )


def change_email_address(
    user_id: UserID,
    new_email_address: Optional[str],
    initiator_id: UserID,
    *,
    reason: Optional[str] = None,
) -> UserEmailAddressChanged:
    """Change the user's e-mail address."""
    user = _get_user(user_id)
    initiator = user_service.get_user(initiator_id)

    old_email_address = user.email_address

    user.email_address = new_email_address
    user.email_address_verified = False

    event_data = {
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
        'initiator_id': str(initiator.id),
    }
    if reason:
        event_data['reason'] = reason

    event = event_service.build_event(
        'user-email-address-changed', user.id, event_data
    )
    db.session.add(event)

    db.session.commit()

    return UserEmailAddressChanged(
        occurred_at=event.occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


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
    initiator_id: UserID,
) -> UserDetailsUpdated:
    """Update the user's details."""
    detail = _get_user_detail(user_id)
    initiator = user_service.get_user(initiator_id)

    old_first_names = detail.first_names
    old_last_name = detail.last_name
    old_date_of_birth = detail.date_of_birth
    old_country = detail.country
    old_zip_code = detail.zip_code
    old_city = detail.city
    old_street = detail.street
    old_phone_number = detail.phone_number

    detail.first_names = first_names
    detail.last_name = last_name
    detail.date_of_birth = date_of_birth
    detail.country = country
    detail.zip_code = zip_code
    detail.city = city
    detail.street = street
    detail.phone_number = phone_number

    event_data = {
        'initiator_id': str(initiator.id),
    }
    _add_if_different(event_data, 'first_names', old_first_names, first_names)
    _add_if_different(event_data, 'last_name', old_last_name, last_name)
    _add_if_different(
        event_data, 'date_of_birth', old_date_of_birth, date_of_birth
    )
    _add_if_different(event_data, 'country', old_country, country)
    _add_if_different(event_data, 'zip_code', old_zip_code, zip_code)
    _add_if_different(event_data, 'city', old_city, city)
    _add_if_different(event_data, 'street', old_street, street)
    _add_if_different(
        event_data, 'phone_number', old_phone_number, phone_number
    )
    event = event_service.build_event(
        'user-details-updated', user_id, event_data
    )
    db.session.add(event)

    db.session.commit()

    user = user_service.get_user(detail.user_id)
    return UserDetailsUpdated(
        occurred_at=event.occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _add_if_different(
    event_data: UserEventData, base_key_name: str, old_value: str, new_value
) -> None:
    if old_value != new_value:
        event_data[f'old_{base_key_name}'] = _to_str_if_not_none(old_value)
        event_data[f'new_{base_key_name}'] = _to_str_if_not_none(new_value)


def _to_str_if_not_none(value: Any) -> Optional[str]:
    return str(value) if (value is not None) else None


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


def _get_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    return user_service.get_db_user(user_id)


def _get_user_detail(user_id: UserID) -> DbUserDetail:
    """Return the user's details, or raise an exception."""
    detail = DbUserDetail.query \
        .filter_by(user_id=user_id) \
        .one_or_none()

    if detail is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return detail
