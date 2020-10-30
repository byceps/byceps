"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.announce.irc import ticketing  # Load signal handlers.
from byceps.events.ticketing import TicketCheckedIn, TicketsSold
from byceps.signals import ticketing as ticketing_signals

from .helpers import (
    assert_submitted_data,
    CHANNEL_ORGA_LOG,
    mocked_irc_bot,
    now,
)


EXPECTED_CHANNEL = CHANNEL_ORGA_LOG


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

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_tickets_sold(app, make_user, admin_user):
    expected_text = 'TreuerKäufer hat 3 Ticket(s) gekauft.'

    user = make_user('TreuerKäufer')

    event = TicketsSold(
        occurred_at=now(),
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        party_id='some-party-id',
        owner_id=user.id,
        owner_screen_name=user.screen_name,
        quantity=3,
    )

    with mocked_irc_bot() as mock:
        ticketing_signals.tickets_sold.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)
