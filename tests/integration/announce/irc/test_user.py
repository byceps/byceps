"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.user import (
    UserAccountCreatedEvent,
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEmailAddressChangedEvent,
    UserEmailAddressInvalidatedEvent,
    UserScreenNameChangedEvent,
)
from byceps.services.site.models import SiteID
from byceps.typing import UserID

from tests.helpers import generate_uuid

from .helpers import build_announcement_request_for_irc, now


OCCURRED_AT = now()
ADMIN_ID = UserID(generate_uuid())
USER_ID = UserID(generate_uuid())


def test_account_created_announced(admin_app: Flask, webhook_for_irc):
    expected_text = 'Jemand hat das Benutzerkonto "JaneDoe" angelegt.'
    expected = build_announcement_request_for_irc(expected_text)

    event = UserAccountCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        user_id=USER_ID,
        user_screen_name='JaneDoe',
        site_id=None,
        site_title=None,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_account_created_announced_on_site(admin_app: Flask, webhook_for_irc):
    expected_text = (
        'Jemand hat das Benutzerkonto "JaneDoeOnSite" '
        'auf Site "ACMECon 2014 website" angelegt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = UserAccountCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        user_id=USER_ID,
        user_screen_name='JaneDoeOnSite',
        site_id=SiteID('acmecon-2014'),
        site_title='ACMECon 2014 website',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_account_created_by_admin_announced(admin_app: Flask, webhook_for_irc):
    expected_text = 'EinAdmin hat das Benutzerkonto "EinUser" angelegt.'
    expected = build_announcement_request_for_irc(expected_text)

    event = UserAccountCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='EinAdmin',
        user_id=USER_ID,
        user_screen_name='EinUser',
        site_id=None,
        site_title=None,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_screen_name_change_announced(admin_app: Flask, webhook_for_irc):
    expected_text = (
        'ElAdmin hat das Benutzerkonto "DrJekyll" in "MrHyde" umbenannt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = UserScreenNameChangedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='ElAdmin',
        user_id=USER_ID,
        old_screen_name='DrJekyll',
        new_screen_name='MrHyde',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_email_address_changed_announced(admin_app: Flask, webhook_for_irc):
    expected_text = (
        'UserSupporter hat die E-Mail-Adresse '
        'des Benutzerkontos "MailboxHopper" geändert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = UserEmailAddressChangedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='UserSupporter',
        user_id=USER_ID,
        user_screen_name='MailboxHopper',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_email_address_invalidated_announced(admin_app: Flask, webhook_for_irc):
    expected_text = (
        'BounceWatchman hat die E-Mail-Adresse '
        'des Benutzerkontos "Faker" invalidiert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = UserEmailAddressInvalidatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='BounceWatchman',
        user_id=USER_ID,
        user_screen_name='Faker',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_user_details_updated_announced(admin_app: Flask, webhook_for_irc):
    expected_text = (
        'Chameleon hat die persönlichen Daten '
        'des Benutzerkontos "Chameleon" geändert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = UserDetailsUpdatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='Chameleon',
        user_id=USER_ID,
        user_screen_name='Chameleon',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_suspended_account_announced(admin_app: Flask, webhook_for_irc):
    expected_text = 'She-Ra hat das Benutzerkonto "Skeletor" gesperrt.'
    expected = build_announcement_request_for_irc(expected_text)

    event = UserAccountSuspendedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='She-Ra',
        user_id=USER_ID,
        user_screen_name='Skeletor',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_unsuspended_account_announced(admin_app: Flask, webhook_for_irc):
    expected_text = 'TheBoss hat das Benutzerkonto "RambaZamba" entsperrt.'
    expected = build_announcement_request_for_irc(expected_text)

    event = UserAccountUnsuspendedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='TheBoss',
        user_id=USER_ID,
        user_screen_name='RambaZamba',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_deleted_account_announced(admin_app: Flask, webhook_for_irc):
    expected_text = (
        f'UberDude hat das Benutzerkonto "Snake" (ID "{USER_ID}") gelöscht.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = UserAccountDeletedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='UberDude',
        user_id=USER_ID,
        user_screen_name='Snake',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected
