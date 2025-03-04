"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.user import (
    user_command_service,
    user_log_service,
    user_service,
)
from byceps.services.user.events import UserEmailAddressChangedEvent


@pytest.fixture(scope='module')
def admin_user(make_user):
    return make_user()


def test_change_email_address_with_reason(admin_app, make_user, admin_user):
    old_email_address = 'zero-cool@users.test'
    new_email_address = 'crash.override@users.test'
    verified = False
    reason = 'Does not want to be recognized by Acid Burn.'

    user = make_user(
        email_address=old_email_address,
        email_address_verified=True,
    )

    user_before = user_service.get_db_user(user.id)
    assert user_before.email_address == old_email_address
    assert user_before.email_address_verified

    log_entries_before = user_log_service.get_entries_for_user(user_before.id)
    assert len(log_entries_before) == 2  # user creation

    # -------------------------------- #

    event = user_command_service.change_email_address(
        user, new_email_address, verified, admin_user, reason=reason
    )

    # -------------------------------- #

    assert isinstance(event, UserEmailAddressChangedEvent)
    assert event.initiator is not None
    assert event.initiator.id == admin_user.id
    assert event.initiator.screen_name == admin_user.screen_name
    assert event.user.id == user.id
    assert event.user.screen_name == user.screen_name

    user_after = user_service.get_db_user(user.id)
    assert user_after.email_address == new_email_address
    assert not user_after.email_address_verified

    log_entries_after = user_log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 3

    user_enabled_log_entry = log_entries_after[-1]
    assert user_enabled_log_entry.event_type == 'user-email-address-changed'
    assert user_enabled_log_entry.data == {
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }


def test_change_email_address_without_reason(admin_app, make_user, admin_user):
    old_email_address = 'address_with_tyop@users.test'
    new_email_address = 'address_without_typo@users.test'
    verified = False

    user = make_user(
        email_address=old_email_address,
        email_address_verified=True,
    )

    # -------------------------------- #

    user_command_service.change_email_address(
        user, new_email_address, verified, admin_user
    )

    # -------------------------------- #

    user_after = user_service.get_db_user(user.id)

    log_entries_after = user_log_service.get_entries_for_user(user_after.id)

    user_enabled_log_entry = log_entries_after[-1]
    assert user_enabled_log_entry.event_type == 'user-email-address-changed'
    assert user_enabled_log_entry.data == {
        'old_email_address': old_email_address,
        'new_email_address': new_email_address,
        'initiator_id': str(admin_user.id),
    }
