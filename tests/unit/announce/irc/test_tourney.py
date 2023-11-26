"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.tourney import (
    TourneyCanceledEvent,
    TourneyFinishedEvent,
    TourneyPausedEvent,
    TourneyStartedEvent,
)

from tests.helpers import generate_uuid

from .helpers import assert_text


TOURNEY_ID = str(generate_uuid())


def test_announce_tourney_started(app: Flask, now: datetime, webhook_for_irc):
    expected_text = 'Tourney Taco Arena (1on1) has been started.'

    event = TourneyStartedEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_paused(app: Flask, now: datetime, webhook_for_irc):
    expected_text = 'Tourney Taco Arena (1on1) has been paused.'

    event = TourneyPausedEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_canceled(app: Flask, now: datetime, webhook_for_irc):
    expected_text = 'Tourney Taco Arena (1on1) has been canceled.'

    event = TourneyCanceledEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_finished(app: Flask, now: datetime, webhook_for_irc):
    expected_text = 'Tourney Taco Arena (1on1) has been finished.'

    event = TourneyFinishedEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
