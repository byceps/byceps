"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.authn.password import authn_password_domain_service


def test_update_password_hash(admin_user, user):
    (
        credential,
        event,
        log_entry,
    ) = authn_password_domain_service.update_password_hash(
        user, 'ReplacementPassw0rd', admin_user
    )

    assert credential.user_id == user.id
    assert credential.password_hash is not None

    assert event.initiator == admin_user
    assert event.user == user

    assert log_entry.event_type == 'password-updated'
    assert log_entry.data == {'initiator_id': str(admin_user.id)}
