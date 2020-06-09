"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.database import db
from byceps.services.authorization import service as authorization_service
from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service

from tests.helpers import create_user_with_detail


@pytest.fixture
def permission():
    permission = authorization_service.create_permission(
        'tickle_mortals', 'Tickle mortals'
    )

    yield permission

    authorization_service.delete_permission(permission.id)


@pytest.fixture
def role(permission):
    role = authorization_service.create_role('demigod', 'Demigod')
    authorization_service.assign_permission_to_role(permission.id, role.id)

    yield role

    authorization_service.delete_role(role.id)


def test_delete_account(admin_app, permission, role, admin_user):
    screen_name = 'GetRidOfMe'
    email_address = 'timedout@users.test'
    legacy_id = 22299

    user = create_user_with_detail(screen_name, email_address=email_address)

    user.legacy_id = legacy_id
    db.session.commit()

    user_id = user.id

    authorization_service.assign_role_to_user(role.id, user_id)

    reason = 'duplicate'

    user_before = user_command_service._get_user(user_id)

    assert user_before.screen_name == screen_name
    assert user_before.email_address == email_address
    assert user_before.deleted == False
    assert user_before.legacy_id == legacy_id

    # details
    assert user_before.detail.first_names is not None
    assert user_before.detail.last_name is not None
    assert user_before.detail.date_of_birth is not None
    assert user_before.detail.country is not None
    assert user_before.detail.zip_code is not None
    assert user_before.detail.city is not None
    assert user_before.detail.street is not None
    assert user_before.detail.phone_number is not None

    # events
    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 1
    assert events_before[0].event_type == 'role-assigned'

    # authorization
    assert authorization_service.find_role_ids_for_user(user_id) == {'demigod'}
    assert authorization_service.get_permission_ids_for_user(user_id) == {
        'tickle_mortals'
    }

    # -------------------------------- #

    user_command_service.delete_account(user_id, admin_user.id, reason=reason)

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)

    assert user_after.screen_name is None
    assert user_after.email_address is None
    assert user_after.deleted == True
    assert user_after.legacy_id is None

    # details
    assert user_after.detail.first_names is None
    assert user_after.detail.last_name is None
    assert user_after.detail.date_of_birth is None
    assert user_after.detail.country is None
    assert user_after.detail.zip_code is None
    assert user_after.detail.city is None
    assert user_after.detail.street is None
    assert user_after.detail.phone_number is None

    # avatar
    assert user_after.avatar_selection is None

    # events
    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 2

    user_enabled_event = events_after[1]
    assert user_enabled_event.event_type == 'user-deleted'
    assert user_enabled_event.data == {
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }

    # authorization
    assert authorization_service.find_role_ids_for_user(user_id) == set()
    assert authorization_service.get_permission_ids_for_user(user_id) == set()

    # Clean up.
    authorization_service.deassign_all_roles_from_user(user.id)
