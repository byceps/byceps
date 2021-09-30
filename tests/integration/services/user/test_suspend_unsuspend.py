"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service
from byceps.services.user import service as user_service


@pytest.fixture(scope='module')
def admin_user(make_user):
    return make_user()


@pytest.fixture
def cheater(make_user):
    return make_user()


@pytest.fixture
def remorseful_user(make_user):
    return make_user()


def test_suspend(admin_app, cheater, admin_user):
    user_id = cheater.id

    reason = 'User has been caught cheating.'

    user_before = user_service.get_user(user_id)
    assert not user_before.suspended

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 1  # user creation

    # -------------------------------- #

    user_command_service.suspend_account(user_id, admin_user.id, reason)

    # -------------------------------- #

    user_after = user_service.get_user(user_id)
    assert user_after.suspended

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 2

    suspended_event = events_after[1]
    assert suspended_event.event_type == 'user-suspended'
    assert suspended_event.data == {
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }


def test_unsuspend(admin_app, remorseful_user, admin_user):
    user_id = remorseful_user.id

    user_command_service.suspend_account(user_id, admin_user.id, 'Annoying')

    reason = 'User showed penitence. Drop the ban.'

    user_before = user_service.get_user(user_id)
    assert user_before.suspended

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 2

    # -------------------------------- #

    user_command_service.unsuspend_account(user_id, admin_user.id, reason)

    # -------------------------------- #

    user_after = user_service.get_user(user_id)
    assert not user_after.suspended

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 3

    unsuspended_event = events_after[2]
    assert unsuspended_event.event_type == 'user-unsuspended'
    assert unsuspended_event.data == {
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }
