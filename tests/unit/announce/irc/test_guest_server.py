"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.core.events import EventParty, EventUser
from byceps.services.guest_server.events import (
    GuestServerApprovedEvent,
    GuestServerCheckedInEvent,
    GuestServerCheckedOutEvent,
    GuestServerRegisteredEvent,
)
from byceps.services.guest_server.models import ServerID

from tests.helpers import generate_uuid

from .helpers import assert_text


SERVER_ID = ServerID(generate_uuid())


def test_guest_server_registered(
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    event_owner: EventUser,
    event_party: EventParty,
    webhook_for_irc,
):
    expected_text = (
        'Admin has registered a guest server owned by Owner '
        'for party ACMECon 2014.'
    )

    event = GuestServerRegisteredEvent(
        occurred_at=now,
        initiator=event_admin,
        party=event_party,
        owner=event_owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_approved(
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    event_owner: EventUser,
    webhook_for_irc,
):
    expected_text = 'Admin has approved a guest server owned by Owner.'

    event = GuestServerApprovedEvent(
        occurred_at=now,
        initiator=event_admin,
        owner=event_owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_in(
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    event_owner: EventUser,
    webhook_for_irc,
):
    expected_text = 'Admin has checked in a guest server owned by Owner.'

    event = GuestServerCheckedInEvent(
        occurred_at=now,
        initiator=event_admin,
        owner=event_owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_out(
    app: BycepsApp,
    now: datetime,
    event_admin: EventUser,
    event_owner: EventUser,
    webhook_for_irc,
):
    expected_text = 'Admin has checked out a guest server owned by Owner.'

    event = GuestServerCheckedOutEvent(
        occurred_at=now,
        initiator=event_admin,
        owner=event_owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def event_admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='Admin')


@pytest.fixture(scope='module')
def event_owner(make_event_user) -> EventUser:
    return make_event_user(screen_name='Owner')


@pytest.fixture(scope='module')
def event_party(make_event_party) -> EventParty:
    return make_event_party(title='ACMECon 2014')
