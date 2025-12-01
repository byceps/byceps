"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.user import user_command_service, user_service
from byceps.services.user.events import UserScreenNameChangedEvent
from byceps.services.user.log import user_log_service


@pytest.fixture(scope='module')
def admin_user(make_user):
    return make_user()


def test_change_screen_name_with_reason(admin_app, make_user, admin_user):
    old_screen_name = 'Zero_Cool'
    new_screen_name = 'Crash_Override'
    reason = 'Do not reveal to Acid Burn.'

    user = make_user(old_screen_name)

    user_before = user_service.get_db_user(user.id)
    assert user_before.screen_name == old_screen_name

    log_entries_before = user_log_service.get_entries_for_user(user_before.id)
    assert len(log_entries_before) == 2  # user creation

    # -------------------------------- #

    event = user_command_service.change_screen_name(
        user, new_screen_name, admin_user, reason=reason
    )

    # -------------------------------- #

    assert isinstance(event, UserScreenNameChangedEvent)
    assert event.initiator is not None
    assert event.initiator.id == admin_user.id
    assert event.initiator.screen_name == admin_user.screen_name
    assert event.user == user
    assert event.old_screen_name == old_screen_name
    assert event.new_screen_name == new_screen_name

    user_after = user_service.get_db_user(user.id)
    assert user_after.screen_name == new_screen_name

    log_entries_after = user_log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 3

    user_enabled_log_entry = log_entries_after[-1]
    assert user_enabled_log_entry.event_type == 'user-screen-name-changed'
    assert user_enabled_log_entry.data == {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'reason': reason,
    }


def test_change_screen_name_without_reason(admin_app, make_user, admin_user):
    old_screen_name = 'NameWithTyop'
    new_screen_name = 'NameWithoutTypo'

    user = make_user(old_screen_name)

    # -------------------------------- #

    user_command_service.change_screen_name(user, new_screen_name, admin_user)

    # -------------------------------- #

    user_after = user_service.get_db_user(user.id)

    log_entries_after = user_log_service.get_entries_for_user(user_after.id)

    user_enabled_log_entry = log_entries_after[-1]
    assert user_enabled_log_entry.event_type == 'user-screen-name-changed'
    assert user_enabled_log_entry.data == {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
    }
