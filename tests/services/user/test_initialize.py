"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest
from pytest import raises

from byceps.services.authorization import service as authorization_service
from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


@pytest.fixture
def uninitialized_user_created_online(db):
    user = create_user('CreatedOnline', initialized=False)
    yield user
    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture
def uninitialized_user_created_at_party_checkin_by_admin(db):
    user = create_user('CreatedAtPartyCheckInByAdmin', initialized=False)
    yield user
    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture
def already_initialized_user(db):
    user = create_user('AlreadyInitialized')
    yield user
    user_command_service.delete_account(user.id, user.id, 'clean up')


@pytest.fixture
def role(
    app,
    uninitialized_user_created_online,
    uninitialized_user_created_at_party_checkin_by_admin,
    already_initialized_user,
):
    role = authorization_service.create_role('board_user', 'Board User')

    yield role

    for user in {
        uninitialized_user_created_online,
        uninitialized_user_created_at_party_checkin_by_admin,
        already_initialized_user,
    }:
        authorization_service.deassign_all_roles_from_user(user.id)

    authorization_service.delete_role(role.id)


def test_initialize_account_as_user(
    app, role, uninitialized_user_created_online
):
    user = uninitialized_user_created_online

    user_before = user_command_service._get_user(user.id)
    assert not user_before.initialized

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    role_ids_before = authorization_service.find_role_ids_for_user(user.id)
    assert role_ids_before == set()

    # -------------------------------- #

    user_command_service.initialize_account(user.id)

    # -------------------------------- #

    user_after = user_command_service._get_user(user.id)
    assert user_after.initialized

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 2

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-initialized'
    assert user_enabled_event.data == {}

    role_assigned_event = events_after[1]
    assert role_assigned_event.event_type == 'role-assigned'
    assert role_assigned_event.data == {
        'role_id': 'board_user',
    }

    role_ids_after = authorization_service.find_role_ids_for_user(user.id)
    assert role_ids_after == {'board_user'}


def test_initialize_account_as_admin(
    app, role, uninitialized_user_created_at_party_checkin_by_admin, admin_user
):
    user = uninitialized_user_created_at_party_checkin_by_admin

    user_before = user_command_service._get_user(user.id)
    assert not user_before.initialized

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    role_ids_before = authorization_service.find_role_ids_for_user(user.id)
    assert role_ids_before == set()

    # -------------------------------- #

    user_command_service.initialize_account(user.id, initiator_id=admin_user.id)

    # -------------------------------- #

    user_after = user_command_service._get_user(user.id)
    assert user_after.initialized

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 2

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-initialized'
    assert user_enabled_event.data == {
        'initiator_id': str(admin_user.id),
    }

    role_assigned_event = events_after[1]
    assert role_assigned_event.event_type == 'role-assigned'
    assert role_assigned_event.data == {
        'initiator_id': str(admin_user.id),
        'role_id': 'board_user',
    }

    role_ids_after = authorization_service.find_role_ids_for_user(user.id)
    assert role_ids_after == {'board_user'}


def test_initialize_already_initialized_account(
    app, role, already_initialized_user, admin_user
):
    user = already_initialized_user

    user_before = user_command_service._get_user(user.id)
    assert user_before.initialized

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    with raises(ValueError):
        user_command_service.initialize_account(
            user.id, initiator_id=admin_user.id
        )

    # -------------------------------- #

    user_after = user_command_service._get_user(user.id)
    assert user_after.initialized  # still initialized

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 0  # no additional user events
