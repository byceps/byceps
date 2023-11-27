"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventParty, EventUser
from byceps.events.guest_server import (
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
    app: Flask,
    now: datetime,
    admin: EventUser,
    owner: EventUser,
    party: EventParty,
    webhook_for_irc,
):
    expected_text = (
        'Admin has registered a guest server owned by Owner '
        'for party ACMECon 2014.'
    )

    event = GuestServerRegisteredEvent(
        occurred_at=now,
        initiator=admin,
        party=party,
        owner=owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_approved(
    app: Flask,
    now: datetime,
    admin: EventUser,
    owner: EventUser,
    webhook_for_irc,
):
    expected_text = 'Admin has approved a guest server owned by Owner.'

    event = GuestServerApprovedEvent(
        occurred_at=now,
        initiator=admin,
        owner=owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_in(
    app: Flask,
    now: datetime,
    admin: EventUser,
    owner: EventUser,
    webhook_for_irc,
):
    expected_text = 'Admin has checked in a guest server owned by Owner.'

    event = GuestServerCheckedInEvent(
        occurred_at=now,
        initiator=admin,
        owner=owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_out(
    app: Flask,
    now: datetime,
    admin: EventUser,
    owner: EventUser,
    webhook_for_irc,
):
    expected_text = 'Admin has checked out a guest server owned by Owner.'

    event = GuestServerCheckedOutEvent(
        occurred_at=now,
        initiator=admin,
        owner=owner,
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='Admin')


@pytest.fixture(scope='module')
def owner(make_event_user) -> EventUser:
    return make_event_user(screen_name='Owner')


@pytest.fixture(scope='module')
def party(make_event_party) -> EventParty:
    return make_event_party(title='ACMECon 2014')
