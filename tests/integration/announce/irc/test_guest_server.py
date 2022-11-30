"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import byceps.announce.connections  # Connect signal handlers.  # noqa: F401
from byceps.services.guest_server import guest_server_service
from byceps.signals import guest_server as guest_server_signals

from .helpers import assert_submitted_data, mocked_irc_bot


def test_guest_server_registered(app, party, admin_user, user):
    expected_text = (
        'Admin hat einen Gastserver von User für die Party "ACMECon 2014" registriert.'
    )

    server, event = guest_server_service.create_server(
        party.id, admin_user.id, user.id
    )

    with mocked_irc_bot() as mock:
        guest_server_signals.guest_server_registered.send(None, event=event)

    assert_submitted_data(mock, expected_text)
