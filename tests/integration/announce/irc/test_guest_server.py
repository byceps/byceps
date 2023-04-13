"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.announce.connections import build_announcement_request
from byceps.services.guest_server import guest_server_service

from .helpers import build_announcement_request_for_irc


def test_guest_server_registered(
    admin_app, party, admin_user, user, webhook_for_irc
):
    expected_text = 'Admin hat einen Gastserver von User für die Party "ACMECon 2014" registriert.'
    expected = build_announcement_request_for_irc(expected_text)

    _, event = guest_server_service.create_server(
        party.id, admin_user.id, user.id
    )

    assert build_announcement_request(event, webhook_for_irc) == expected
