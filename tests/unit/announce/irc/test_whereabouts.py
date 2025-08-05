"""
:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.core.events import EventParty
from byceps.services.whereabouts.events import (
    WhereaboutsClientApprovedEvent,
    WhereaboutsClientDeletedEvent,
    WhereaboutsClientRegisteredEvent,
    WhereaboutsClientSignedOffEvent,
    WhereaboutsClientSignedOnEvent,
    WhereaboutsStatusUpdatedEvent,
)
from byceps.services.whereabouts.models import WhereaboutsClientID

from .helpers import assert_text


CLIENT_ID = WhereaboutsClientID(UUID('371aba195a922c74c5b1273766bca016'))


def test_whereabouts_client_registered(
    app: BycepsApp,
    now: datetime,
    make_event_user,
    webhook_for_irc,
):
    expected_text = f'Whereabouts client "{CLIENT_ID}" has been registered.'

    event = WhereaboutsClientRegisteredEvent(
        occurred_at=now,
        initiator=None,
        client_id=CLIENT_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_whereabouts_client_approved(
    app: BycepsApp,
    now: datetime,
    make_event_user,
    webhook_for_irc,
):
    expected_text = f'Admin has approved whereabouts client "{CLIENT_ID}".'

    initiator = make_event_user(screen_name='Admin')

    event = WhereaboutsClientApprovedEvent(
        occurred_at=now,
        initiator=initiator,
        client_id=CLIENT_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_whereabouts_client_deleted(
    app: BycepsApp,
    now: datetime,
    make_event_user,
    webhook_for_irc,
):
    expected_text = f'Admin has deleted whereabouts client "{CLIENT_ID}".'

    initiator = make_event_user(screen_name='Admin')

    event = WhereaboutsClientDeletedEvent(
        occurred_at=now,
        initiator=initiator,
        client_id=CLIENT_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_whereabouts_client_signed_on(
    app: BycepsApp, now: datetime, webhook_for_irc
):
    expected_text = f'Whereabouts client "{CLIENT_ID}" has signed on.'

    event = WhereaboutsClientSignedOnEvent(
        occurred_at=now,
        initiator=None,
        client_id=CLIENT_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_whereabouts_client_signed_off(
    app: BycepsApp, now: datetime, webhook_for_irc
):
    expected_text = f'Whereabouts client "{CLIENT_ID}" has signed off.'

    event = WhereaboutsClientSignedOffEvent(
        occurred_at=now,
        initiator=None,
        client_id=CLIENT_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_whereabouts_status_updated(
    app: BycepsApp,
    now: datetime,
    party: EventParty,
    make_event_user,
    webhook_for_irc,
):
    expected_text = 'Dingo\'s whereabouts changed to "backstage area".'

    user = make_event_user(screen_name='Dingo')

    event = WhereaboutsStatusUpdatedEvent(
        occurred_at=now,
        initiator=user,
        party=party,
        user=user,
        whereabouts_description='backstage area',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
