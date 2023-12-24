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
    TourneyMatchReadyEvent,
    TourneyMatchResetEvent,
    TourneyMatchScoreConfirmedEvent,
    TourneyMatchScoreRandomizedEvent,
    TourneyMatchScoreSubmittedEvent,
)

from tests.helpers import generate_uuid

from .helpers import assert_text


MATCH_ID = str(generate_uuid())


def test_announce_match_ready(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant1: EventTourneyParticipant,
    participant2: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        'Match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8) '
        'is ready to be played.'
    )

    event = TourneyMatchReadyEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant1=participant1,
        participant2=participant2,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_reset(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant1: EventTourneyParticipant,
    participant2: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        'Match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8) '
        'has been reset.'
    )

    event = TourneyMatchResetEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant1=participant1,
        participant2=participant2,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_score_submitted(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant1: EventTourneyParticipant,
    participant2: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        'A result has been entered '
        'for match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8).'
    )

    event = TourneyMatchScoreSubmittedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant1=participant1,
        participant2=participant2,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_score_confirmed(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant1: EventTourneyParticipant,
    participant2: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        'The result '
        'for match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8) '
        'has been confirmed.'
    )

    event = TourneyMatchScoreConfirmedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant1=participant1,
        participant2=participant2,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_score_randomized(
    app: Flask,
    now: datetime,
    tourney: EventTourney,
    participant1: EventTourneyParticipant,
    participant2: EventTourneyParticipant,
    webhook_for_irc,
):
    expected_text = (
        'A random result has been entered '
        'for match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8).'
    )

    event = TourneyMatchScoreRandomizedEvent(
        occurred_at=now,
        initiator=None,
        tourney=tourney,
        match_id=MATCH_ID,
        participant1=participant1,
        participant2=participant2,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def tourney(make_event_tourney) -> EventTourney:
    return make_event_tourney(title='Octo-Highlander (8on8)')


@pytest.fixture(scope='module')
def participant1(make_event_tourney_participant) -> EventTourneyParticipant:
    return make_event_tourney_participant(name='Die Einen')


@pytest.fixture(scope='module')
def participant2(make_event_tourney_participant) -> EventTourneyParticipant:
    return make_event_tourney_participant(name='Die Anderen')
