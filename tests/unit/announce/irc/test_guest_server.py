"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.guest_server import GuestServerRegisteredEvent
from byceps.services.guest_server.models import ServerID
from byceps.typing import PartyID, UserID

from tests.helpers import generate_uuid

from .helpers import build_announcement_request_for_irc, now


OCCURRED_AT = now()
ADMIN_ID = UserID(generate_uuid())
USER_ID = UserID(generate_uuid())


def test_guest_server_registered(app: Flask, webhook_for_irc):
    expected_text = 'Admin hat einen Gastserver von User für die Party "ACMECon 2014" registriert.'
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected
