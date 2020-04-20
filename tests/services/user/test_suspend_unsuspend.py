"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service
from byceps.services.user import service as user_service

from tests.helpers import create_user

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


def test_suspend(app, admin_user):
    user = create_user('Cheater')
    user_id = user.id

    reason = 'User has been caught cheating.'

    user_before = user_service.find_user(user_id)
    assert not user_before.suspended

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    user_command_service.suspend_account(user_id, admin_user.id, reason)

    # -------------------------------- #

    user_after = user_service.find_user(user_id)
    assert user_after.suspended

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 1

    suspended_event = events_after[0]
    assert suspended_event.event_type == 'user-suspended'
    assert suspended_event.data == {
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }


def test_unsuspend(app, admin_user):
    user = create_user('TemporaryNuisance')
    user_id = user.id

    user_command_service.suspend_account(user_id, admin_user.id, 'Annoying')

    reason = 'User showed penitence. Drop the ban.'

    user_before = user_service.find_user(user_id)
    assert user_before.suspended

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 1

    # -------------------------------- #

    user_command_service.unsuspend_account(user_id, admin_user.id, reason)

    # -------------------------------- #

    user_after = user_service.find_user(user_id)
    assert not user_after.suspended

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 2

    unsuspended_event = events_after[1]
    assert unsuspended_event.event_type == 'user-unsuspended'
    assert unsuspended_event.data == {
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }
