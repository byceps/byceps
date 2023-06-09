"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.tourney import (
    TourneyCanceledEvent,
    TourneyFinishedEvent,
    TourneyPausedEvent,
    TourneyStartedEvent,
)

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
TOURNEY_ID = str(generate_uuid())


def test_announce_tourney_started(app: Flask, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde gestartet.'

    event = TourneyStartedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_paused(app: Flask, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde unterbrochen.'

    event = TourneyPausedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_canceled(app: Flask, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde abgesagt.'

    event = TourneyCanceledEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_tourney_finished(app: Flask, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde beendet.'

    event = TourneyFinishedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Taco Arena (1on1)',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
