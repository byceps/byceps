"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from unittest.mock import patch

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventUser
from byceps.events.ticketing import TicketCheckedInEvent, TicketsSoldEvent
from byceps.services.party.models import PartyID
from byceps.services.ticketing.models.ticket import (
    TicketCode,
    TicketID,
    TicketSaleStats,
)

from tests.helpers import generate_uuid

from .helpers import assert_text


def test_ticket_checked_in(
    app: Flask,
    now: datetime,
    admin: EventUser,
    make_event_user,
    webhook_for_irc,
):
    expected_text = (
        'TicketingAdmin has checked in ticket "GTFIN", used by Teilnehmer.'
    )

    event = TicketCheckedInEvent(
        occurred_at=now,
        initiator=admin,
        ticket_id=TicketID(generate_uuid()),
        ticket_code=TicketCode('GTFIN'),
        occupied_seat_id=None,
        user=make_event_user(screen_name='Teilnehmer'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_single_ticket_sold(
    get_ticket_sale_stats_mock,
    app: Flask,
    now: datetime,
    admin: EventUser,
    make_event_user,
    webhook_for_irc,
):
    expected_text = (
        'Neuling has paid 1 ticket. '
        'Currently 772 of 1001 tickets have been paid.'
    )

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=772,
    )

    event = TicketsSoldEvent(
        occurred_at=now,
        initiator=admin,
        party_id=PartyID('popular-party'),
        owner=make_event_user(screen_name='Neuling'),
        quantity=1,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_multiple_tickets_sold(
    get_ticket_sale_stats_mock,
    app: Flask,
    now: datetime,
    admin: EventUser,
    make_event_user,
    webhook_for_irc,
):
    expected_text = (
        'TreuerKäufer has paid 3 tickets. '
        'Currently 775 of 1001 tickets have been paid.'
    )

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=775,
    )

    event = TicketsSoldEvent(
        occurred_at=now,
        initiator=admin,
        party_id=PartyID('popular-party'),
        owner=make_event_user(screen_name='TreuerKäufer'),
        quantity=3,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='TicketingAdmin')
