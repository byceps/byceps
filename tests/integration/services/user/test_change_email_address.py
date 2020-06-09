"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.events.user import UserEmailAddressChanged
from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service

from tests.helpers import create_user


@pytest.fixture(scope='module')
def admin_user(make_user):
    return make_user('EmailAddressAdmin')


def test_change_email_address_with_reason(admin_app, admin_user):
    old_email_address = 'zero-cool@users.test'
    new_email_address = 'crash.override@users.test'
    reason = 'Does not want to be recognized by Acid Burn.'

    user_id = create_user(
        'WantsEmailAddressChangedWithReason',
        email_address=old_email_address,
        email_address_verified=True,
    ).id

    user_before = user_command_service._get_user(user_id)
    assert user_before.email_address == old_email_address
    assert user_before.email_address_verified

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    event = user_command_service.change_email_address(
        user_id, new_email_address, admin_user.id, reason=reason
    )

    # -------------------------------- #

    assert isinstance(event, UserEmailAddressChanged)
    assert event.user_id == user_id
    assert event.initiator_id == admin_user.id

    user_after = user_command_service._get_user(user_id)
    assert user_after.email_address == new_email_address
    assert not user_after.email_address_verified

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 1

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-email-address-changed'
    assert user_enabled_event.data == {
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }

    user_command_service.delete_account(user_id, user_id, 'clean up')


def test_change_email_address_without_reason(admin_app, admin_user):
    old_email_address = 'address_with_tyop@users.test'
    new_email_address = 'address_without_typo@users.test'

    user_id = create_user(
        'WantsEmailAddressChangedWithoutReason',
        email_address=old_email_address,
        email_address_verified=True,
    ).id

    # -------------------------------- #

    user_command_service.change_email_address(
        user_id, new_email_address, admin_user.id
    )

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)

    events_after = event_service.get_events_for_user(user_after.id)

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-email-address-changed'
    assert user_enabled_event.data == {
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
        'initiator_id': str(admin_user.id),
    }

    user_command_service.delete_account(user_id, user_id, 'clean up')
