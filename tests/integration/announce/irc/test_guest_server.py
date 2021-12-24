"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import byceps.announce.connections  # Connect signal handlers.
from byceps.services.guest_server import service as guest_server_service
from byceps.signals import guest_server as guest_server_signals

from .helpers import assert_submitted_data, CHANNEL_INTERNAL, mocked_irc_bot


EXPECTED_CHANNEL = CHANNEL_INTERNAL


def test_guest_server_registered(app, party, admin_user, user):
    expected_text = (
        'Admin hat einen Gastserver von User für die Party "ACMECon 2014" registriert.'
    )

    server, event = guest_server_service.create_server(
        party.id, admin_user.id, user.id
    )

    with mocked_irc_bot() as mock:
        guest_server_signals.guest_server_registered.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)
