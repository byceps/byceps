"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.user.events import (
    UserAccountCreatedEvent,
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserEmailAddressInvalidatedEvent,
    UserScreenNameChangedEvent,
)
from byceps.services.user.models.user import UserDetailDifference

from .helpers import assert_text


def test_account_created_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'Someone has created user account "JaneDoe".'

    event = UserAccountCreatedEvent(
        occurred_at=now,
        initiator=None,
        user=make_user(screen_name='JaneDoe'),
        site=None,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_account_created_announced_on_site(
    app: BycepsApp,
    now: datetime,
    make_event_site,
    make_user,
    webhook_for_irc,
):
    expected_text = (
        'Someone has created user account "JaneDoeOnSite" '
        'on site "ACMECon 2014 website".'
    )

    event = UserAccountCreatedEvent(
        occurred_at=now,
        initiator=None,
        user=make_user(screen_name='JaneDoeOnSite'),
        site=make_event_site(title='ACMECon 2014 website'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_account_created_by_admin_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'EinAdmin has created user account "EinUser".'

    event = UserAccountCreatedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='EinAdmin'),
        user=make_user(screen_name='EinUser'),
        site=None,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_screen_name_change_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'ElAdmin has renamed user account "DrJekyll" to "MrHyde".'

    event = UserScreenNameChangedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='ElAdmin'),
        user=make_user(screen_name='MrHyde'),
        old_screen_name='DrJekyll',
        new_screen_name='MrHyde',
        reason='The serum.',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_email_address_changed_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = (
        'UserSupporter has changed the email address '
        'of user account "MailboxHopper".'
    )

    event = UserEmailAddressChangedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='UserSupporter'),
        user=make_user(screen_name='MailboxHopper'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_email_address_invalidated_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = (
        'BounceWatchman has invalidated the email address '
        'of user account "Faker".'
    )

    event = UserEmailAddressInvalidatedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='BounceWatchman'),
        user=make_user(screen_name='Faker'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_user_details_updated_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = (
        'Chameleon has changed personal data '
        '(date of birth, postal code, city, street) '
        'of user account "Chameleon".'
    )

    event = UserDetailsUpdatedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='Chameleon'),
        user=make_user(screen_name='Chameleon'),
        fields={
            'date_of_birth': UserDetailDifference(old=None, new='1986-04-26'),
            'postal_code': UserDetailDifference(old='22999', new='20099'),
            'city': UserDetailDifference(old='Büttenwarder', new='Hamburg'),
            'street': UserDetailDifference(old='Südweg 7', new='Raboisen 1'),
        },
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_suspended_account_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'She-Ra has suspended user account "Skeletor".'

    event = UserAccountSuspendedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='She-Ra'),
        user=make_user(screen_name='Skeletor'),
        reason='Is a supervillain.',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_unsuspended_account_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'TheBoss has unsuspended user account "RambaZamba".'

    event = UserAccountUnsuspendedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='TheBoss'),
        user=make_user(screen_name='RambaZamba'),
        reason='This is fine.',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_deleted_account_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    user = make_user(screen_name='Snake')

    expected_text = (
        f'Uberino has deleted user account "Snake" (ID "{user.id}").'
    )

    event = UserAccountDeletedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='Uberino'),
        user=user,
        reason='Sus',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
