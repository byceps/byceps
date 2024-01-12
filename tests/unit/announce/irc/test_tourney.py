"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.tourney import (
    EventTourney,
    TourneyCanceledEvent,
    TourneyFinishedEvent,
    TourneyPausedEvent,
    TourneyStartedEvent,
)

from .helpers import assert_text


def test_announce_tourney_started(
    app: Flask, now: datetime, tourney: EventTourney, webhook_for_irc
):
    expected_text = 'Tourney Taco Arena (1on1) has been started.'

    event = TourneyStartedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_paused(
    app: Flask, now: datetime, tourney: EventTourney, webhook_for_irc
):
    expected_text = 'Tourney Taco Arena (1on1) has been paused.'

    event = TourneyPausedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_canceled(
    app: Flask, now: datetime, tourney: EventTourney, webhook_for_irc
):
    expected_text = 'Tourney Taco Arena (1on1) has been canceled.'

    event = TourneyCanceledEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_finished(
    app: Flask, now: datetime, tourney: EventTourney, webhook_for_irc
):
    expected_text = 'Tourney Taco Arena (1on1) has been finished.'

    event = TourneyFinishedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def tourney(make_event_tourney) -> EventTourney:
    return make_event_tourney(title='Taco Arena (1on1)')
