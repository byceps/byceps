"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service

from tests.helpers import create_user

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            _app = admin_app

            admin = create_user('Administrator')
            _app.admin_id = admin.id

            yield _app


def test_change_screen_name_with_reason(app):
    admin_id = app.admin_id

    old_screen_name = 'Zero_Cool'
    new_screen_name = 'Crash_Override'
    reason = 'Do not reveal to Acid Burn.'

    user_id = create_user(old_screen_name).id

    user_before = user_command_service._get_user(user_id)
    assert user_before.screen_name == old_screen_name

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    user_command_service.change_screen_name(
        user_id, new_screen_name, admin_id, reason=reason
    )

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)
    assert user_after.screen_name == new_screen_name

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 1

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-screen-name-changed'
    assert user_enabled_event.data == {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'initiator_id': str(admin_id),
        'reason': reason,
    }


def test_change_screen_name_without_reason(app):
    admin_id = app.admin_id

    old_screen_name = 'NameWithTyop'
    new_screen_name = 'NameWithoutTypo'

    user_id = create_user(old_screen_name).id

    # -------------------------------- #

    user_command_service.change_screen_name(user_id, new_screen_name, admin_id)

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)

    events_after = event_service.get_events_for_user(user_after.id)

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-screen-name-changed'
    assert user_enabled_event.data == {
        'old_screen_name': old_screen_name,
        'new_screen_name': new_screen_name,
        'initiator_id': str(admin_id),
    }
