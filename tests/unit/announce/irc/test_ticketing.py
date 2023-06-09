"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.ticketing import TicketCheckedInEvent, TicketsSoldEvent
from byceps.services.ticketing.models.ticket import TicketCode, TicketSaleStats
from byceps.typing import PartyID, UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
ADMIN_ID = UserID(generate_uuid())
USER_ID = UserID(generate_uuid())


def test_ticket_checked_in(app: Flask, webhook_for_irc):
    expected_text = 'TicketingAdmin hat Ticket "GTFIN", genutzt von Teilnehmer, eingecheckt.'

    event = TicketCheckedInEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='TicketingAdmin',
        ticket_id=None,
        ticket_code=TicketCode('GTFIN'),
        occupied_seat_id=None,
        user_id=USER_ID,
        user_screen_name='Teilnehmer',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_single_ticket_sold(
    get_ticket_sale_stats_mock, app: Flask, webhook_for_irc
):
    expected_text = (
        'Neuling hat 1 Ticket bezahlt. '
        'Aktuell sind 772 von 1001 Tickets bezahlt.'
    )

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=772,
    )

    event = TicketsSoldEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='TicketingAdmin',
        party_id=PartyID('popular-party'),
        owner_id=USER_ID,
        owner_screen_name='Neuling',
        quantity=1,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_multiple_tickets_sold(
    get_ticket_sale_stats_mock, app: Flask, webhook_for_irc
):
    expected_text = (
        'TreuerKäufer hat 3 Tickets bezahlt. '
        'Aktuell sind 775 von 1001 Tickets bezahlt.'
    )

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=775,
    )

    event = TicketsSoldEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='TicketingAdmin',
        party_id=PartyID('popular-party'),
        owner_id=USER_ID,
        owner_screen_name='TreuerKäufer',
        quantity=3,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
