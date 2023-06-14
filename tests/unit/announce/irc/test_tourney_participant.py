"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.tourney import (
    TourneyParticipantDisqualifiedEvent,
    TourneyParticipantEliminatedEvent,
    TourneyParticipantReadyEvent,
    TourneyParticipantWarnedEvent,
)

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
TOURNEY_ID = str(generate_uuid())
MATCH_ID = str(generate_uuid())
PARTICIPANT_ID = generate_token()
PARTICIPANT_NAME = 'Le Supern00bs'


def test_announce_participant_ready(app: Flask, webhook_for_irc):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) ist spielbereit.'
    )

    event = TourneyParticipantReadyEvent(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_eliminated(app: Flask, webhook_for_irc):
    expected_text = '"Le Supern00bs" ist aus dem Turnier Burrito Blaster (3on3) ausgeschieden.'

    event = TourneyParticipantEliminatedEvent(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_warned(app: Flask, webhook_for_irc):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) '
        'wurde verwarnt. \x038,8 \x03'
    )

    event = TourneyParticipantWarnedEvent(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_participant_disqualified(app: Flask, webhook_for_irc):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) '
        'wurde disqualifiziert. \x034,4 \x03'
    )

    event = TourneyParticipantDisqualifiedEvent(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Burrito Blaster (3on3)',
        match_id=MATCH_ID,
        participant_id=PARTICIPANT_ID,
        participant_name=PARTICIPANT_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
