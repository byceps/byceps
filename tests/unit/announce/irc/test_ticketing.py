"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.events.base import EventParty, EventUser
from byceps.events.ticketing import TicketCheckedInEvent, TicketsSoldEvent
from byceps.services.party.models import Party
from byceps.services.ticketing.models.ticket import (
    TicketCode,
    TicketID,
    TicketSaleStats,
)

from tests.helpers import generate_uuid

from .helpers import assert_text


def test_ticket_checked_in(
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    make_event_user,
    webhook_for_irc,
):
    expected_text = (
        'TicketingAdmin has checked in ticket "GTFIN", used by Teilnehmer.'
    )

    event = TicketCheckedInEvent(
        occurred_at=now,
        initiator=event_admin,
        ticket_id=TicketID(generate_uuid()),
        ticket_code=TicketCode('GTFIN'),
        occupied_seat_id=None,
        user=make_event_user(screen_name='Teilnehmer'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.party.party_service.get_party')
@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_single_ticket_sold_without_max(
    get_ticket_sale_stats_mock,
    get_party_mock,
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    party: Party,
    event_party: EventParty,
    make_event_user,
    webhook_for_irc,
):
    expected_text = (
        'Neuling has paid for 1 ticket. '
        'Currently 772 tickets have been sold.'
    )

    get_party_mock.return_value = party

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=None,
        tickets_sold=772,
    )

    event = TicketsSoldEvent(
        occurred_at=now,
        initiator=event_admin,
        party=event_party,
        owner=make_event_user(screen_name='Neuling'),
        quantity=1,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.party.party_service.get_party')
@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_single_ticket_sold_with_max(
    get_ticket_sale_stats_mock,
    get_party_mock,
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    party: Party,
    event_party: EventParty,
    make_event_user,
    webhook_for_irc,
):
    expected_text = (
        'Neuling has paid for 1 ticket. '
        'Currently 772 of 1001 tickets have been sold.'
    )

    get_party_mock.return_value = party

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=772,
    )

    event = TicketsSoldEvent(
        occurred_at=now,
        initiator=event_admin,
        party=event_party,
        owner=make_event_user(screen_name='Neuling'),
        quantity=1,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.party.party_service.get_party')
@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_multiple_tickets_sold(
    get_ticket_sale_stats_mock,
    get_party_mock,
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    party: Party,
    event_party: EventParty,
    make_event_user,
    webhook_for_irc,
):
    expected_text = (
        'TreuerKäufer has paid for 3 tickets. '
        'Currently 775 of 1001 tickets have been sold.'
    )

    get_party_mock.return_value = party

    get_ticket_sale_stats_mock.return_value = TicketSaleStats(
        tickets_max=1001,
        tickets_sold=775,
    )

    event = TicketsSoldEvent(
        occurred_at=now,
        initiator=event_admin,
        party=event_party,
        owner=make_event_user(screen_name='TreuerKäufer'),
        quantity=3,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def event_admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='TicketingAdmin')


@pytest.fixture(scope='module')
def event_party(make_event_party, party: Party) -> EventParty:
    return make_event_party(id=party.id, title=party.title)
