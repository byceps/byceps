"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.events.tourney import (
    TourneyParticipantReady,
    TourneyParticipantEliminated,
    TourneyParticipantWarned,
    TourneyParticipantDisqualified,
)
from byceps.signals import tourney as tourney_signals

from ..helpers import (
    assert_submitted_data,
    CHANNEL_PUBLIC,
    mocked_irc_bot,
    now,
)


EXPECTED_CHANNEL = CHANNEL_PUBLIC


def test_announce_participant_ready(app, tourney, match, participant):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) ist spielbereit.'
    )

    event = TourneyParticipantReady(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant_id=participant.id,
        participant_name=participant.name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.participant_ready.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_participant_eliminated(app, tourney, match, participant):
    expected_text = (
        '"Le Supern00bs" ist aus dem Turnier Burrito Blaster (3on3) ausgeschieden.'
    )

    event = TourneyParticipantEliminated(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant_id=participant.id,
        participant_name=participant.name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.participant_eliminated.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_participant_warned(app, tourney, match, participant):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) '
        'wurde verwarnt. \x038,8 \x03'
    )

    event = TourneyParticipantWarned(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant_id=participant.id,
        participant_name=participant.name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.participant_warned.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_participant_disqualified(app, tourney, match, participant):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) '
        'wurde disqualifiziert. \x034,4 \x03'
    )

    event = TourneyParticipantDisqualified(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant_id=participant.id,
        participant_name=participant.name,
    )

    with mocked_irc_bot() as mock:
        tourney_signals.participant_disqualified.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


# helpers


@pytest.fixture(scope='module')
def tourney(make_tourney):
    return make_tourney('T-77', 'Burrito Blaster (3on3)')


@pytest.fixture(scope='module')
def participant(make_participant):
    return make_participant('P-119', 'Le Supern00bs')


@pytest.fixture(scope='module')
def another_participant(make_participant):
    return make_participant('P-160', 'Rndm Plrs')


@pytest.fixture(scope='module')
def match(make_match, tourney, participant, another_participant):
    return make_match('M-25', tourney, participant, another_participant)
