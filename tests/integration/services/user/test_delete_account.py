"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authorization import authz_service
from byceps.services.user import (
    user_deletion_service,
    user_log_service,
    user_service,
)


@pytest.fixture
def role():
    role = authz_service.create_role('demigod', 'Demigod')
    authz_service.assign_permission_to_role('board.view_hidden', role.id)

    yield role

    authz_service.delete_role(role.id)


def test_delete_account(admin_app, role, make_user):
    screen_name = 'GetRidOfMe'
    email_address = 'timedout@users.test'
    legacy_id = 'user-22299'

    user = make_user(
        screen_name, email_address=email_address, legacy_id=legacy_id
    )

    admin_user = make_user()

    user_id = user.id

    authz_service.assign_role_to_user(role.id, user_id)

    reason = 'duplicate'

    user_before = user_service.get_db_user(user_id)

    assert user_before.screen_name == screen_name
    assert user_before.email_address == email_address
    assert not user_before.deleted
    assert user_before.legacy_id == legacy_id

    # details
    assert user_before.detail.first_name is not None
    assert user_before.detail.last_name is not None
    assert user_before.detail.date_of_birth is not None
    assert user_before.detail.country is not None
    assert user_before.detail.zip_code is not None
    assert user_before.detail.city is not None
    assert user_before.detail.street is not None
    assert user_before.detail.phone_number is not None

    # log entries
    log_entries_before = user_log_service.get_entries_for_user(user_before.id)
    assert len(log_entries_before) == 2
    assert log_entries_before[1].event_type == 'role-assigned'

    # authorization
    assert authz_service.find_role_ids_for_user(user_id) == {'demigod'}
    assert authz_service.get_permission_ids_for_user(user_id) == {
        'board.view_hidden'
    }

    # -------------------------------- #

    user_deletion_service.delete_account(user_id, admin_user.id, reason=reason)

    # -------------------------------- #

    user_after = user_service.get_db_user(user_id)

    assert user_after.screen_name is None
    assert user_after.email_address is None
    assert user_after.avatar_id is None
    assert user_after.avatar is None
    assert user_after.deleted
    assert user_after.legacy_id is None

    # details
    assert user_after.detail.first_name is None
    assert user_after.detail.last_name is None
    assert user_after.detail.date_of_birth is None
    assert user_after.detail.country is None
    assert user_after.detail.zip_code is None
    assert user_after.detail.city is None
    assert user_after.detail.street is None
    assert user_after.detail.phone_number is None

    # log entries
    log_entries_after = user_log_service.get_entries_for_user(user_after.id)
    assert len(log_entries_after) == 3

    user_enabled_log_entry = log_entries_after[2]
    assert user_enabled_log_entry.event_type == 'user-deleted'
    assert user_enabled_log_entry.data == {
        'initiator_id': str(admin_user.id),
        'reason': reason,
    }

    # authorization
    assert authz_service.find_role_ids_for_user(user_id) == set()
    assert authz_service.get_permission_ids_for_user(user_id) == set()
