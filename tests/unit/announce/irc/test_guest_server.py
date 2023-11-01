"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.guest_server import (
    GuestServerApprovedEvent,
    GuestServerCheckedInEvent,
    GuestServerCheckedOutEvent,
    GuestServerRegisteredEvent,
)
from byceps.services.guest_server.models import ServerID
from byceps.services.party.models import PartyID
from byceps.services.user.models.user import UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
ADMIN_ID = UserID(generate_uuid())
USER_ID = UserID(generate_uuid())


def test_guest_server_registered(app: Flask, webhook_for_irc):
    expected_text = (
        'Admin has registered a guest server owned by User '
        'for party ACMECon 2014.'
    )

    event = GuestServerRegisteredEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='Admin',
        party_id=PartyID('acmecon-2014'),
        party_title='ACMECon 2014',
        owner_id=USER_ID,
        owner_screen_name='User',
        server_id=ServerID(generate_uuid()),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_approved(app: Flask, webhook_for_irc):
    expected_text = 'Admin has approved a guest server owned by User.'

    event = GuestServerApprovedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='Admin',
        owner_id=USER_ID,
        owner_screen_name='User',
        server_id=ServerID(generate_uuid()),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_in(app: Flask, webhook_for_irc):
    expected_text = 'Admin has checked in a guest server owned by User.'

    event = GuestServerCheckedInEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='Admin',
        owner_id=USER_ID,
        owner_screen_name='User',
        server_id=ServerID(generate_uuid()),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_out(app: Flask, webhook_for_irc):
    expected_text = 'Admin has checked out a guest server owned by User.'

    event = GuestServerCheckedOutEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='Admin',
        owner_id=USER_ID,
        owner_screen_name='User',
        server_id=ServerID(generate_uuid()),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
