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


def test_enable(app):
    admin_id = app.admin_id
    user_id = create_user('Enable-Me', enabled=False).id

    user_before = user_command_service._get_user(user_id)
    assert not user_before.enabled

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    user_command_service.enable_user(user_id, admin_id)

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)
    assert user_after.enabled

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 1

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-enabled'
    assert user_enabled_event.data == {
        'initiator_id': str(admin_id),
    }


def test_disable(app):
    admin_id = app.admin_id
    user_id = create_user('Disable-Me', enabled=True).id

    user_before = user_command_service._get_user(user_id)
    assert user_before.enabled

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    user_command_service.disable_user(user_id, admin_id)

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)
    assert not user_after.enabled

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 1

    user_disabled_event = events_after[0]
    assert user_disabled_event.event_type == 'user-disabled'
    assert user_disabled_event.data == {
        'initiator_id': str(admin_id),
    }
