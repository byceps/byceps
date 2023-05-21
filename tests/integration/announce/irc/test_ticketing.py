"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

from byceps.announce.connections import build_announcement_request
from byceps.events.ticketing import TicketCheckedInEvent, TicketsSoldEvent
from byceps.services.ticketing.models.ticket import TicketSaleStats

from .helpers import build_announcement_request_for_irc, now


def test_ticket_checked_in(admin_app, make_user, admin_user, webhook_for_irc):
    expected_text = (
        'Admin hat Ticket "GTFIN", genutzt von Einchecker, eingecheckt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    user = make_user('Einchecker')

    event = TicketCheckedInEvent(
        occurred_at=now(),
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        ticket_id=None,
        ticket_code='GTFIN',
        occupied_seat_id=None,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_single_ticket_sold(
    get_ticket_sale_stats_mock,
    admin_app,
    make_user,
    admin_user,
    webhook_for_irc,
):
    expected_text = (
        'Neuling hat 1 Ticket bezahlt. '
        'Aktuell sind 772 von 1001 Tickets bezahlt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=772,
    )

    user = make_user('Neuling')

    event = TicketsSoldEvent(
        occurred_at=now(),
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        party_id='popular-party',
        owner_id=user.id,
        owner_screen_name=user.screen_name,
        quantity=1,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_multiple_tickets_sold(
    get_ticket_sale_stats_mock,
    admin_app,
    make_user,
    admin_user,
    webhook_for_irc,
):
    expected_text = (
        'TreuerKäufer hat 3 Tickets bezahlt. '
        'Aktuell sind 775 von 1001 Tickets bezahlt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=775,
    )

    user = make_user('TreuerKäufer')

    event = TicketsSoldEvent(
        occurred_at=now(),
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        party_id='popular-party',
        owner_id=user.id,
        owner_screen_name=user.screen_name,
        quantity=3,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected
