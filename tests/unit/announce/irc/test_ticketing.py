"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.ticketing import TicketCheckedInEvent, TicketsSoldEvent
from byceps.services.party.models import PartyID
from byceps.services.ticketing.models.ticket import TicketCode, TicketSaleStats
from byceps.services.user.models.user import User

from .helpers import assert_text, now


OCCURRED_AT = now()


def test_ticket_checked_in(app: Flask, admin: User, make_user, webhook_for_irc):
    expected_text = (
        'TicketingAdmin has checked in ticket "GTFIN", used by Teilnehmer.'
    )

    event = TicketCheckedInEvent(
        occurred_at=OCCURRED_AT,
        initiator=admin,
        ticket_id=None,
        ticket_code=TicketCode('GTFIN'),
        occupied_seat_id=None,
        user=make_user(screen_name='Teilnehmer'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_single_ticket_sold(
    get_ticket_sale_stats_mock,
    app: Flask,
    admin: User,
    make_user,
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
        occurred_at=OCCURRED_AT,
        initiator=admin,
        party_id=PartyID('popular-party'),
        owner=make_user(screen_name='Neuling'),
        quantity=1,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


@patch('byceps.services.ticketing.ticket_service.get_ticket_sale_stats')
def test_multiple_tickets_sold(
    get_ticket_sale_stats_mock,
    app: Flask,
    admin: User,
    make_user,
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
        occurred_at=OCCURRED_AT,
        initiator=admin,
        party_id=PartyID('popular-party'),
        owner=make_user(screen_name='TreuerKäufer'),
        quantity=3,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_user) -> User:
    return make_user(screen_name='TicketingAdmin')
