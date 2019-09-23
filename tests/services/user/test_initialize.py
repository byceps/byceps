"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest
from pytest import raises

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


def test_initialize_account(app):
    admin_id = app.admin_id
    user_id = create_user('CreatedAtPartyCheckIn', initialized=False).id

    user_before = user_command_service._get_user(user_id)
    assert not user_before.initialized

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    user_command_service.initialize_account(user_id, admin_id)

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)
    assert user_after.initialized

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 1

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-initialized'
    assert user_enabled_event.data == {
        'initiator_id': str(admin_id),
    }


def test_initialize_already_initialized_account(app):
    admin_id = app.admin_id
    user_id = create_user('AlreadyInitialized').id

    user_before = user_command_service._get_user(user_id)
    assert user_before.initialized

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    with raises(ValueError):
        user_command_service.initialize_account(user_id, admin_id)

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)
    assert user_after.initialized  # still initialized

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 0  # no additional user events
