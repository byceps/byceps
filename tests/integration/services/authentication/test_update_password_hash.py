"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.authentication.password import authn_password_service
from byceps.services.authentication.password.dbmodels import DbCredential
from byceps.services.user import user_log_service


def test_update_password_hash(site_app, admin_user, make_user):
    user = make_user(password='InitialPassw0rd')

    admin_id = admin_user.id
    user_id = user.id

    password_hash_before = get_password_hash(user_id)
    assert password_hash_before is not None

    log_entries_before = user_log_service.get_entries_for_user(user_id)
    assert len(log_entries_before) == 1  # user creation

    # -------------------------------- #

    event = authn_password_service.update_password_hash(
        user, 'ReplacementPassw0rd', admin_user
    )

    # -------------------------------- #

    password_hash_after = get_password_hash(user_id)
    assert password_hash_after is not None
    assert password_hash_after != password_hash_before

    assert event.user_id == user.id
    assert event.user_screen_name == user.screen_name
    assert event.initiator_id == admin_user.id
    assert event.initiator_screen_name == admin_user.screen_name

    log_entries_after = user_log_service.get_entries_for_user(user_id)
    assert len(log_entries_after) == 2

    password_updated_log_entry = log_entries_after[1]
    assert password_updated_log_entry.event_type == 'password-updated'
    assert password_updated_log_entry.data == {
        'initiator_id': str(admin_id),
    }


# helpers


def get_password_hash(user_id):
    credential = db.session.get(DbCredential, user_id)
    return credential.password_hash
