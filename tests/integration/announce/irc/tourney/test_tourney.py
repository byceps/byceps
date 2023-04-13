"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.announce.connections import build_announcement_request
from byceps.events.tourney import (
    TourneyCanceled,
    TourneyFinished,
    TourneyPaused,
    TourneyStarted,
)

from ..helpers import build_announcement_request_for_irc, now


def test_announce_tourney_started(admin_app, tourney, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde gestartet.'
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyStarted(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_tourney_paused(admin_app, tourney, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde unterbrochen.'
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyPaused(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_tourney_canceled(admin_app, tourney, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde abgesagt.'
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyCanceled(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_tourney_finished(admin_app, tourney, webhook_for_irc):
    expected_text = 'Das Turnier Taco Arena (1on1) wurde beendet.'
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyFinished(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


# helpers


@pytest.fixture(scope='module')
def tourney(make_tourney):
    return make_tourney('T-37', 'Taco Arena (1on1)')
