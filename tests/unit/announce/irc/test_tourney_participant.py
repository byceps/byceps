"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.tourney import (
    TourneyParticipantDisqualifiedEvent,
    TourneyParticipantEliminatedEvent,
    TourneyParticipantReadyEvent,
    TourneyParticipantWarnedEvent,
)

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text


TOURNEY_ID = str(generate_uuid())
MATCH_ID = str(generate_uuid())
PARTICIPANT_ID = generate_token()
PARTICIPANT_NAME = 'Le Supern00bs'


def test_announce_participant_ready(app: Flask, now: datetime, webhook_for_irc):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) is ready to play.'
    )

    event = TourneyParticipantReadyEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_eliminated(
    app: Flask, now: datetime, webhook_for_irc
):
    expected_text = (
        '"Le Supern00bs" has been eliminated '
        'from tourney Burrito Blaster (3on3).'
    )

    event = TourneyParticipantEliminatedEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_warned(
    app: Flask, now: datetime, webhook_for_irc
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) '
        'has been warned. \x038,8 \x03'
    )

    event = TourneyParticipantWarnedEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_disqualified(
    app: Flask, now: datetime, webhook_for_irc
):
    expected_text = (
        '"Le Supern00bs" in tourney Burrito Blaster (3on3) '
        'has been disqualified. \x034,4 \x03'
    )

    event = TourneyParticipantDisqualifiedEvent(
        occurred_at=now,
        initiator=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
