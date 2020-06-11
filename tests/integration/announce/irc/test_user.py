"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.announce.irc import user  # Load signal handlers.
import byceps.blueprints.user.signals as user_signals
from byceps.events.user import (
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from byceps.services.user import command_service as user_command_service

from .helpers import (
    assert_submitted_data,
    CHANNEL_ORGA_LOG,
    CHANNEL_PUBLIC,
    mocked_irc_bot,
    now,
)


EXPECTED_CHANNELS = [CHANNEL_ORGA_LOG]


def test_account_created_announced(app, make_user):
    expected_text = 'Jemand hat das Benutzerkonto "JaneDoe" angelegt.'

    user = make_user('JaneDoe')

    with mocked_irc_bot() as mock:
        event = UserAccountCreated(
            occurred_at=now(), user_id=user.id, initiator_id=None
        )
        user_signals.account_created.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_account_created_by_admin_announced(app, make_user):
    expected_text = 'EinAdmin hat das Benutzerkonto "EinUser" angelegt.'

    admin = make_user('EinAdmin')
    user = make_user('EinUser')

    with mocked_irc_bot() as mock:
        event = UserAccountCreated(
            occurred_at=now(), user_id=user.id, initiator_id=admin.id
        )
        user_signals.account_created.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_screen_name_change_announced(app, make_user):
    expected_text = (
        'ElAdmin hat das Benutzerkonto "DrJekyll" in "MrHyde" umbenannt.'
    )

    admin = make_user('ElAdmin')
    user = make_user('DrJekyll')

    with mocked_irc_bot() as mock:
        event = UserScreenNameChanged(
            occurred_at=now(),
            user_id=user.id,
            old_screen_name=user.screen_name,
            new_screen_name='MrHyde',
            initiator_id=admin.id,
        )
        user_signals.screen_name_changed.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_email_address_invalidated_announced(app, make_user):
    expected_text = (
        'BounceWatchman hat die E-Mail-Adresse '
        'des Benutzerkontos "Faker" invalidiert.'
    )

    admin = make_user('BounceWatchman')
    user = make_user('Faker')

    with mocked_irc_bot() as mock:
        event = UserEmailAddressInvalidated(
            occurred_at=now(), user_id=user.id, initiator_id=admin.id,
        )
        user_signals.email_address_invalidated.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_user_details_updated_announced(app, make_user):
    expected_text = (
        'Chameleon hat die persönlichen Daten '
        'des Benutzerkontos "Chameleon" geändert.'
    )

    user = make_user('Chameleon')

    with mocked_irc_bot() as mock:
        event = UserDetailsUpdated(
            occurred_at=now(), user_id=user.id, initiator_id=user.id,
        )
        user_signals.details_updated.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_suspended_account_announced(app, make_user):
    expected_text = 'She-Ra hat das Benutzerkonto "Skeletor" gesperrt.'

    admin = make_user('She-Ra')
    user = make_user('Skeletor')

    with mocked_irc_bot() as mock:
        event = UserAccountSuspended(
            occurred_at=now(), user_id=user.id, initiator_id=admin.id
        )
        user_signals.account_suspended.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_unsuspended_account_announced(app, make_user):
    expected_text = 'TheBoss hat das Benutzerkonto "RambaZamba" entsperrt.'

    admin = make_user('TheBoss')
    user = make_user('RambaZamba')

    with mocked_irc_bot() as mock:
        event = UserAccountUnsuspended(
            occurred_at=now(), user_id=user.id, initiator_id=admin.id
        )
        user_signals.account_unsuspended.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)


def test_deleted_account_announced(app, make_user):
    expected_text = (
        'UberDude hat das Benutzerkonto mit der ID '
        '"76b0c57f-8909-4b02-90c9-96e0a817f738" gelöscht.'
    )

    admin = make_user('UberDude')
    user = make_user('Snake', user_id='76b0c57f-8909-4b02-90c9-96e0a817f738')

    with mocked_irc_bot() as mock:
        user_command_service.delete_account(
            user.id, admin.id, 'specious reason'
        )

        event = UserAccountDeleted(
            occurred_at=now(), user_id=user.id, initiator_id=admin.id
        )
        user_signals.account_deleted.send(None, event=event)

        assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)
