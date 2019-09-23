"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import UUID

import pytest

from byceps.services.user import command_service as user_command_service
from byceps.services.user import event_service

from tests.helpers import create_user, create_user_with_detail

from ...conftest import database_recreated


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            _app = admin_app

            admin = create_user('Administrator')
            _app.admin_id = admin.id

            yield _app


def test_delete_account(app, db):
    admin_id = app.admin_id

    user_id = UUID('20868b15-b935-40fc-8054-38854ef8509a')
    screen_name = 'GetRidOfMe'
    email_address = 'timedout@example.net'
    legacy_id = 22299

    user = create_user_with_detail(
        screen_name,
        user_id=user_id,
        email_address=email_address,
    )

    user.legacy_id = legacy_id
    db.session.commit()

    reason = 'duplicate'

    user_before = user_command_service._get_user(user_id)

    assert user_before.screen_name == screen_name
    assert user_before.email_address == email_address
    assert user_before.deleted == False
    assert user_before.legacy_id == legacy_id

    assert user_before.detail.first_names is not None
    assert user_before.detail.last_name is not None
    assert user_before.detail.date_of_birth is not None
    assert user_before.detail.country is not None
    assert user_before.detail.zip_code is not None
    assert user_before.detail.city is not None
    assert user_before.detail.street is not None
    assert user_before.detail.phone_number is not None

    events_before = event_service.get_events_for_user(user_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    user_command_service.delete_account(user_id, admin_id, reason=reason)

    # -------------------------------- #

    user_after = user_command_service._get_user(user_id)

    assert user_after.screen_name == 'deleted-20868b15b93540fc805438854ef8509a'
    assert user_after.email_address == '20868b15b93540fc805438854ef8509a@user.invalid'
    assert user_after.deleted == True
    assert user_after.legacy_id is None

    assert user_after.detail.first_names is None
    assert user_after.detail.last_name is None
    assert user_after.detail.date_of_birth is None
    assert user_after.detail.country is None
    assert user_after.detail.zip_code is None
    assert user_after.detail.city is None
    assert user_after.detail.street is None
    assert user_after.detail.phone_number is None

    assert user_after.avatar_selection is None

    events_after = event_service.get_events_for_user(user_after.id)
    assert len(events_after) == 1

    user_enabled_event = events_after[0]
    assert user_enabled_event.event_type == 'user-deleted'
    assert user_enabled_event.data == {
        'initiator_id': str(admin_id),
        'reason': reason,
    }
