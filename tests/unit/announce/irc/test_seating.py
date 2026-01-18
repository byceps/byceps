"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.seating.events import (
    SeatGroupOccupiedEvent,
    SeatGroupReleasedEvent,
)
from byceps.services.seating.models import SeatGroupID
from byceps.services.ticketing.models.ticket import TicketBundleID
from byceps.services.user.models.user import User

from tests.helpers import generate_uuid

from .helpers import assert_text


def test_seat_group_occupied(
    app: BycepsApp,
    now: datetime,
    admin_user: User,
    make_user,
    webhook_for_irc,
):
    seat_group_id = SeatGroupID(generate_uuid())
    ticket_bundle_id = TicketBundleID(generate_uuid())
    ticket_bundle_owner = make_user(screen_name='ClanLeader')

    expected_text = (
        'SeatingAdmin has occupied seat group "Clan Area 1" '
        f'with ticket bundle {ticket_bundle_id} owned by ClanLeader.'
    )

    event = SeatGroupOccupiedEvent(
        occurred_at=now,
        initiator=admin_user,
        seat_group_id=seat_group_id,
        seat_group_title='Clan Area 1',
        ticket_bundle_id=ticket_bundle_id,
        ticket_bundle_owner=ticket_bundle_owner,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_seat_group_released(
    app: BycepsApp,
    now: datetime,
    admin_user: User,
    webhook_for_irc,
):
    seat_group_id = SeatGroupID(generate_uuid())

    expected_text = 'SeatingAdmin has released seat group "Clan Area 1".'

    event = SeatGroupReleasedEvent(
        occurred_at=now,
        initiator=admin_user,
        seat_group_id=seat_group_id,
        seat_group_title='Clan Area 1',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin_user(make_user) -> User:
    return make_user(screen_name='SeatingAdmin')
