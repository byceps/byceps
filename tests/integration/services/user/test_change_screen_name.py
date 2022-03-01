"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.events.user import UserScreenNameChanged
from byceps.services.user import command_service as user_command_service
from byceps.services.user import log_service


@pytest.fixture(scope='module')
def admin_user(make_user):
    return make_user()


def test_change_screen_name_with_reason(admin_app, make_user, admin_user):
    old_screen_name = 'Zero_Cool'
    new_screen_name = 'Crash_Override'
    reason = 'Do not reveal to Acid Burn.'

    user_id = make_user(old_screen_name).id

    user_before = user_command_service._get_user(user_id)
    assert user_before.screen_name == old_screen_name

    log_entries_before = log_service.get_entries_for_user(user_before.id)
    assert len(log_entries_before) == 1  # user creation

    # -------------------------------- #

    event = user_command_service.change_screen_name(
        user_id, new_screen_name, admin_user.id, reason=reason
    )

    # -------------------------------- #

    assert isinstance(event, UserScreenNameChanged)
    assert event.user_id == user_id
    assert event.initiator_id == admin_user.id
    assert event.initiator_screen_name == admin_user.screen_name
    assert event.old_screen_name == old_screen_name
    assert event.new_screen_name == new_screen_name

    user_after = user_command_service._get_user(user_id)
    assert user_after.screen_name == new_screen_name

    log_entries_after = log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 2

    user_enabled_log_entry = log_entries_after[1]
    assert user_enabled_log_entry.event_type == 'user-screen-name-changed'
    assert user_enabled_log_entry.data == {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }


def test_change_screen_name_without_reason(admin_app, make_user, admin_user):
    old_screen_name = 'NameWithTyop'
    new_screen_name = 'NameWithoutTypo'

    user_id = make_user(old_screen_name).id

    # -------------------------------- #

    user_command_service.change_screen_name(
        user_id, new_screen_name, admin_user.id
    )

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)

    log_entries_after = log_service.get_entries_for_user(user_after.id)

    user_enabled_log_entry = log_entries_after[1]
    assert user_enabled_log_entry.event_type == 'user-screen-name-changed'
    assert user_enabled_log_entry.data == {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'initiator_id': str(admin_user.id),
    }
