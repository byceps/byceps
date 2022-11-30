"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.  # noqa: F401
from byceps.events.tourney import (
    TourneyCanceled,
    TourneyFinished,
    TourneyPaused,
    TourneyStarted,
)
from byceps.signals import tourney as tourney_signals

from ..helpers import assert_submitted_text, mocked_irc_bot, now


def test_announce_tourney_started(app, tourney):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde gestartet.'

    event = TourneyStarted(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.tourney_started.send(None, event=event)

    assert_submitted_text(mock, expected_text)


def test_announce_tourney_paused(app, tourney):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde unterbrochen.'

    event = TourneyPaused(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.tourney_paused.send(None, event=event)

    assert_submitted_text(mock, expected_text)


def test_announce_tourney_canceled(app, tourney):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde abgesagt.'

    event = TourneyCanceled(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.tourney_canceled.send(None, event=event)

    assert_submitted_text(mock, expected_text)


def test_announce_tourney_finished(app, tourney):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde beendet.'

    event = TourneyFinished(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.tourney_finished.send(None, event=event)

    assert_submitted_text(mock, expected_text)


# helpers


@pytest.fixture(scope='module')
def tourney(make_tourney):
    return make_tourney('T-37', 'Taco Arena (1on1)')
