"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.irc.connections  # Connect signal handlers.
from byceps.events.tourney import (
    TourneyMatchReady,
    TourneyMatchReset,
    TourneyMatchScoreSubmitted,
    TourneyMatchScoreConfirmed,
    TourneyMatchScoreRandomized,
)
from byceps.signals import tourney as tourney_signals

from ..helpers import (
    assert_submitted_data,
    CHANNEL_PUBLIC,
    mocked_irc_bot,
    now,
)


EXPECTED_CHANNEL = CHANNEL_PUBLIC


def test_announce_match_ready(app, tourney, match):
    expected_text = (
        'Das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'kann gespielt werden.'
    )

    event = TourneyMatchReady(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant1_id=match.participant1_id,
        participant1_name=match.participant1_name,
        participant2_id=match.participant2_id,
        participant2_name=match.participant2_name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.match_ready.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_match_reset(app, tourney, match):
    expected_text = (
        'Das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde zurückgesetzt.'
    )

    event = TourneyMatchReset(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant1_id=match.participant1_id,
        participant1_name=match.participant1_name,
        participant2_id=match.participant2_id,
        participant2_name=match.participant2_name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.match_reset.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_match_score_submitted(app, tourney, match):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde ein Ergebnis eingetragen.'
    )

    event = TourneyMatchScoreSubmitted(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant1_id=match.participant1_id,
        participant1_name=match.participant1_name,
        participant2_id=match.participant2_id,
        participant2_name=match.participant2_name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.match_score_submitted.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_match_score_confirmed(app, tourney, match):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde das eingetragene Ergebnis bestätigt.'
    )

    event = TourneyMatchScoreConfirmed(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant1_id=match.participant1_id,
        participant1_name=match.participant1_name,
        participant2_id=match.participant2_id,
        participant2_name=match.participant2_name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.match_score_confirmed.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_match_score_randomized(app, tourney, match):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde ein zufälliges Ergebnis eingetragen.'
    )

    event = TourneyMatchScoreRandomized(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant1_id=match.participant1_id,
        participant1_name=match.participant1_name,
        participant2_id=match.participant2_id,
        participant2_name=match.participant2_name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.match_score_randomized.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


# helpers


@pytest.fixture(scope='module')
def tourney(make_tourney):
    return make_tourney('T-49', 'Octo-Highlander (8on8)')


@pytest.fixture(scope='module')
def participant1(make_participant):
    return make_participant('P-134', 'Die Einen')


@pytest.fixture(scope='module')
def participant2(make_participant):
    return make_participant('P-257', 'Die Anderen')


@pytest.fixture(scope='module')
def match(make_match, tourney, participant1, participant2):
    return make_match('M-18', tourney, participant1, participant2)
