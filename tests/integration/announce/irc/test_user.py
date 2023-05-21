"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.announce.connections import build_announcement_request
from byceps.events.user import (
    UserAccountCreatedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserEmailAddressInvalidatedEvent,
    UserScreenNameChangedEvent,
)
from byceps.services.user import user_deletion_service

from .helpers import build_announcement_request_for_irc, now


def test_account_created_announced(admin_app, make_user, webhook_for_irc):
    expected_text = 'Jemand hat das Benutzerkonto "JaneDoe" angelegt.'
    expected = build_announcement_request_for_irc(expected_text)

    user = make_user('JaneDoe')

    event = UserAccountCreatedEvent(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        user_id=user.id,
        user_screen_name=user.screen_name,
        site_id=None,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_account_created_announced_on_site(
    admin_app, make_user, site, webhook_for_irc
):
    expected_text = (
        'Jemand hat das Benutzerkonto "JaneDoeOnSite" '
        'auf Site "ACMECon 2014 website" angelegt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    user = make_user('JaneDoeOnSite')

    event = UserAccountCreatedEvent(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        user_id=user.id,
        user_screen_name=user.screen_name,
        site_id=site.id,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_account_created_by_admin_announced(
    admin_app, make_user, webhook_for_irc
):
    expected_text = 'EinAdmin hat das Benutzerkonto "EinUser" angelegt.'
    expected = build_announcement_request_for_irc(expected_text)

    admin = make_user('EinAdmin')
    user = make_user('EinUser')

    event = UserAccountCreatedEvent(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
        site_id=None,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_screen_name_change_announced(admin_app, make_user, webhook_for_irc):
    expected_text = (
        'ElAdmin hat das Benutzerkonto "DrJekyll" in "MrHyde" umbenannt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    admin = make_user('ElAdmin')
    user = make_user('DrJekyll')

    event = UserScreenNameChangedEvent(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        old_screen_name=user.screen_name,
        new_screen_name='MrHyde',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_email_address_changed_announced(admin_app, make_user, webhook_for_irc):
    expected_text = (
        'UserSupporter hat die E-Mail-Adresse '
        'des Benutzerkontos "MailboxHopper" geändert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    admin = make_user('UserSupporter')
    user = make_user('MailboxHopper')

    event = UserEmailAddressChangedEvent(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_email_address_invalidated_announced(
    admin_app, make_user, webhook_for_irc
):
    expected_text = (
        'BounceWatchman hat die E-Mail-Adresse '
        'des Benutzerkontos "Faker" invalidiert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    admin = make_user('BounceWatchman')
    user = make_user('Faker')

    event = UserEmailAddressInvalidatedEvent(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_user_details_updated_announced(admin_app, make_user, webhook_for_irc):
    expected_text = (
        'Chameleon hat die persönlichen Daten '
        'des Benutzerkontos "Chameleon" geändert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    user = make_user('Chameleon')

    event = UserDetailsUpdatedEvent(
        occurred_at=now(),
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_suspended_account_announced(admin_app, make_user, webhook_for_irc):
    expected_text = 'She-Ra hat das Benutzerkonto "Skeletor" gesperrt.'
    expected = build_announcement_request_for_irc(expected_text)

    admin = make_user('She-Ra')
    user = make_user('Skeletor')

    event = UserAccountSuspendedEvent(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_unsuspended_account_announced(admin_app, make_user, webhook_for_irc):
    expected_text = 'TheBoss hat das Benutzerkonto "RambaZamba" entsperrt.'
    expected = build_announcement_request_for_irc(expected_text)

    admin = make_user('TheBoss')
    user = make_user('RambaZamba')

    event = UserAccountUnsuspendedEvent(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_deleted_account_announced(admin_app, make_user, webhook_for_irc):
    admin = make_user('UberDude')
    user = make_user('Snake')

    expected_text = (
        f'UberDude hat das Benutzerkonto "Snake" (ID "{user.id}") gelöscht.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = user_deletion_service.delete_account(
        user.id, admin.id, 'specious reason'
    )

    assert build_announcement_request(event, webhook_for_irc) == expected
