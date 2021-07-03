"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.authentication.password.dbmodels import (
    Credential as DbCredential,
)
from byceps.services.authentication.password import service as password_service
from byceps.services.user import event_service


def test_update_password_hash(site_app, admin_user, make_user):
    user = make_user('PasswordHashUpdater', password='InitialPassw0rd')

    admin_id = admin_user.id
    user_id = user.id

    password_hash_before = get_password_hash(user_id)
    assert password_hash_before is not None

    events_before = event_service.get_events_for_user(user_id)
    assert len(events_before) == 0

    # -------------------------------- #

    password_service.update_password_hash(
        user_id, 'ReplacementPassw0rd', admin_id
    )

    # -------------------------------- #

    password_hash_after = get_password_hash(user_id)
    assert password_hash_after is not None
    assert password_hash_after != password_hash_before

    events_after = event_service.get_events_for_user(user_id)
    assert len(events_after) == 1

    password_updated_event = events_after[0]
    assert password_updated_event.event_type == 'password-updated'
    assert password_updated_event.data == {
        'initiator_id': str(admin_id),
    }

    # Clean up.
    password_service.delete_password_hash(user_id)


# helpers


def get_password_hash(user_id):
    credential = db.session.query(DbCredential).get(user_id)
    return credential.password_hash
