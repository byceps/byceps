"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventUser
from byceps.events.guest_server import (
    GuestServerApprovedEvent,
    GuestServerCheckedInEvent,
    GuestServerCheckedOutEvent,
    GuestServerRegisteredEvent,
)
from byceps.services.guest_server.models import ServerID
from byceps.services.party.models import PartyID
from byceps.services.user.models.user import User

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
SERVER_ID = ServerID(generate_uuid())


def test_guest_server_registered(
    app: Flask, admin: User, owner: User, webhook_for_irc
):
    expected_text = (
        'Admin has registered a guest server owned by Owner '
        'for party ACMECon 2014.'
    )

    event = GuestServerRegisteredEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(admin),
        party_id=PartyID('acmecon-2014'),
        party_title='ACMECon 2014',
        owner=EventUser.from_user(owner),
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_approved(
    app: Flask, admin: User, owner: User, webhook_for_irc
):
    expected_text = 'Admin has approved a guest server owned by Owner.'

    event = GuestServerApprovedEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(admin),
        owner=EventUser.from_user(owner),
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_in(
    app: Flask, admin: User, owner: User, webhook_for_irc
):
    expected_text = 'Admin has checked in a guest server owned by Owner.'

    event = GuestServerCheckedInEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(admin),
        owner=EventUser.from_user(owner),
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_guest_server_checked_out(
    app: Flask, admin: User, owner: User, webhook_for_irc
):
    expected_text = 'Admin has checked out a guest server owned by Owner.'

    event = GuestServerCheckedOutEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(admin),
        owner=EventUser.from_user(owner),
        server_id=SERVER_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_user) -> User:
    return make_user(screen_name='Admin')


@pytest.fixture(scope='module')
def owner(make_user) -> User:
    return make_user(screen_name='Owner')
