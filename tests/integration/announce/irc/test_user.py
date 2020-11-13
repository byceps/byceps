"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.announce.irc import user  # Load signal handlers.
from byceps.events.user import (
    UserAccountCreated,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from byceps.services.user import command_service as user_command_service
from byceps.signals import user as user_signals

from .helpers import (
    assert_submitted_data,
    CHANNEL_ORGA_LOG,
    CHANNEL_PUBLIC,
    mocked_irc_bot,
    now,
)


EXPECTED_CHANNEL = CHANNEL_ORGA_LOG


def test_account_created_announced(app, make_user):
    expected_text = 'Jemand hat das Benutzerkonto "JaneDoe" angelegt.'

    user = make_user('JaneDoe')

    event = UserAccountCreated(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    with mocked_irc_bot() as mock:
        user_signals.account_created.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_account_created_by_admin_announced(app, make_user):
    expected_text = 'EinAdmin hat das Benutzerkonto "EinUser" angelegt.'

    admin = make_user('EinAdmin')
    user = make_user('EinUser')

    event = UserAccountCreated(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    with mocked_irc_bot() as mock:
        user_signals.account_created.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_screen_name_change_announced(app, make_user):
    expected_text = (
        'ElAdmin hat das Benutzerkonto "DrJekyll" in "MrHyde" umbenannt.'
    )

    admin = make_user('ElAdmin')
    user = make_user('DrJekyll')

    event = UserScreenNameChanged(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        old_screen_name=user.screen_name,
        new_screen_name='MrHyde',
    )

    with mocked_irc_bot() as mock:
        user_signals.screen_name_changed.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_email_address_invalidated_announced(app, make_user):
    expected_text = (
        'BounceWatchman hat die E-Mail-Adresse '
        'des Benutzerkontos "Faker" invalidiert.'
    )

    admin = make_user('BounceWatchman')
    user = make_user('Faker')

    event = UserEmailAddressInvalidated(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    with mocked_irc_bot() as mock:
        user_signals.email_address_invalidated.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_user_details_updated_announced(app, make_user):
    expected_text = (
        'Chameleon hat die persönlichen Daten '
        'des Benutzerkontos "Chameleon" geändert.'
    )

    user = make_user('Chameleon')

    event = UserDetailsUpdated(
        occurred_at=now(),
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    with mocked_irc_bot() as mock:
        user_signals.details_updated.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_suspended_account_announced(app, make_user):
    expected_text = 'She-Ra hat das Benutzerkonto "Skeletor" gesperrt.'

    admin = make_user('She-Ra')
    user = make_user('Skeletor')

    event = UserAccountSuspended(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    with mocked_irc_bot() as mock:
        user_signals.account_suspended.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_unsuspended_account_announced(app, make_user):
    expected_text = 'TheBoss hat das Benutzerkonto "RambaZamba" entsperrt.'

    admin = make_user('TheBoss')
    user = make_user('RambaZamba')

    event = UserAccountUnsuspended(
        occurred_at=now(),
        initiator_id=admin.id,
        initiator_screen_name=admin.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    with mocked_irc_bot() as mock:
        user_signals.account_unsuspended.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_deleted_account_announced(app, make_user):
    expected_text = (
        'UberDude hat das Benutzerkonto "Snake" '
        '(ID "76b0c57f-8909-4b02-90c9-96e0a817f738") gelöscht.'
    )

    admin = make_user('UberDude')
    user = make_user('Snake', user_id='76b0c57f-8909-4b02-90c9-96e0a817f738')

    event = user_command_service.delete_account(
        user.id, admin.id, 'specious reason'
    )

    with mocked_irc_bot() as mock:
        user_signals.account_deleted.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)
