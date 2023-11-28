"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.tourney import (
    EventTourney,
    EventTourneyParticipant,
    TourneyParticipantDisqualifiedEvent,
    TourneyParticipantEliminatedEvent,
    TourneyParticipantReadyEvent,
    TourneyParticipantWarnedEvent,
)

from tests.helpers import generate_uuid

from .helpers import assert_text


MATCH_ID = str(generate_uuid())


def test_announce_participant_ready(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) is ready to play.'
    )

    event = TourneyParticipantReadyEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant=participant,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_eliminated(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" has been eliminated '
        'from tourney Burrito Blaster (3on3).'
    )

    event = TourneyParticipantEliminatedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant=participant,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_warned(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) '
        'has been warned. \x038,8 \x03'
    )

    event = TourneyParticipantWarnedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant=participant,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_disqualified(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) '
        'has been disqualified. \x034,4 \x03'
    )

    event = TourneyParticipantDisqualifiedEvent(
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
def tourney(make_event_tourney) -> EventTourney:
    return make_event_tourney(title='Burrito Blaster (3on3)')


@pytest.fixture(scope='module')
def participant(make_event_tourney_participant) -> EventTourneyParticipant:
    return make_event_tourney_participant(name='Le Supern00bs')
