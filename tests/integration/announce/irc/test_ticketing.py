"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.announce.irc import ticketing  # Load signal handlers.
from byceps.events.ticketing import TicketCheckedIn
from byceps.signals import ticketing as ticketing_signals

from .helpers import (
    assert_submitted_data,
    CHANNEL_ORGA_LOG,
    mocked_irc_bot,
    now,
)


EXPECTED_CHANNELS = [CHANNEL_ORGA_LOG]


def test_ticket_checked_in(app, make_user, admin_user):
    expected_text = (
        'Admin hat Ticket "GTFIN", benutzt von Einchecker, eingecheckt.'
    )

    user = make_user('Einchecker')

    event = TicketCheckedIn(
        occurred_at=now(),
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        ticket_id=None,
        ticket_code='GTFIN',
        occupied_seat_id=None,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    with mocked_irc_bot() as mock:
        ticketing_signals.ticket_checked_in.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNELS, expected_text)
