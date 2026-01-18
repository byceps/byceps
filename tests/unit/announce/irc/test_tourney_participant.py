"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.tourney.events import (
    EventTourneyParticipant,
    TourneyMatchParticipantDisqualifiedEvent,
    TourneyMatchParticipantEliminatedEvent,
    TourneyMatchParticipantReadyEvent,
    TourneyMatchParticipantWarnedEvent,
)
from byceps.services.tourney.models import BasicTourney, MatchID

from tests.helpers import generate_uuid

from .helpers import assert_text


MATCH_ID = MatchID(generate_uuid())


def test_announce_participant_ready(
    app: BycepsApp,
    now: datetime,
    tourney: BasicTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) is ready to play.'
    )

    event = TourneyMatchParticipantReadyEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant=participant,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_eliminated(
    app: BycepsApp,
    now: datetime,
    tourney: BasicTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" has been eliminated '
        'from tourney Burrito Blaster (3on3).'
    )

    event = TourneyMatchParticipantEliminatedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant=participant,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_warned(
    app: BycepsApp,
    now: datetime,
    tourney: BasicTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) '
        'has been warned. \x038,8 \x03'
    )

    event = TourneyMatchParticipantWarnedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant=participant,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_disqualified(
    app: BycepsApp,
    now: datetime,
    tourney: BasicTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) '
        'has been disqualified. \x034,4 \x03'
    )

    event = TourneyMatchParticipantDisqualifiedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant=participant,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def tourney(make_basic_tourney) -> BasicTourney:
    return make_basic_tourney(title='Burrito Blaster (3on3)')


@pytest.fixture(scope='module')
def participant(make_event_tourney_participant) -> EventTourneyParticipant:
    return make_event_tourney_participant(name='Le Supern00bs')
