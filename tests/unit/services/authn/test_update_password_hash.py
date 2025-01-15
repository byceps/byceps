"""
:Copyright: 2014-2025 Jochen Kupperschmidt
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

    assert event.initiator is not None
    assert event.initiator.id == admin_user.id
    assert event.initiator.screen_name == admin_user.screen_name
    assert event.user.id == user.id
    assert event.user.screen_name == user.screen_name

    assert log_entry.event_type == 'password-updated'
    assert log_entry.data == {'initiator_id': str(admin_user.id)}
