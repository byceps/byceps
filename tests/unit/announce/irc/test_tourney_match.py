"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.tourney import (
    TourneyMatchReadyEvent,
    TourneyMatchResetEvent,
    TourneyMatchScoreConfirmedEvent,
    TourneyMatchScoreRandomizedEvent,
    TourneyMatchScoreSubmittedEvent,
)

from tests.helpers import generate_token, generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
TOURNEY_ID = str(generate_uuid())
MATCH_ID = str(generate_uuid())
PARTICIPANT_1_ID = generate_token()
PARTICIPANT_1_NAME = 'Die Einen'
PARTICIPANT_2_ID = generate_token()
PARTICIPANT_2_NAME = 'Die Anderen'


def test_announce_match_ready(app: Flask, webhook_for_irc):
    expected_text = (
        'Match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8) '
        'is ready to be played.'
    )

    event = TourneyMatchReadyEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Octo-Highlander (8on8)',
        match_id=MATCH_ID,
        participant1_id=PARTICIPANT_1_ID,
        participant1_name=PARTICIPANT_1_NAME,
        participant2_id=PARTICIPANT_2_ID,
        participant2_name=PARTICIPANT_2_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_reset(app: Flask, webhook_for_irc):
    expected_text = (
        'Match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8) '
        'has been reset.'
    )

    event = TourneyMatchResetEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Octo-Highlander (8on8)',
        match_id=MATCH_ID,
        participant1_id=PARTICIPANT_1_ID,
        participant1_name=PARTICIPANT_1_NAME,
        participant2_id=PARTICIPANT_2_ID,
        participant2_name=PARTICIPANT_2_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_score_submitted(app: Flask, webhook_for_irc):
    expected_text = (
        'A result has been entered '
        'for match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8).'
    )

    event = TourneyMatchScoreSubmittedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Octo-Highlander (8on8)',
        match_id=MATCH_ID,
        participant1_id=PARTICIPANT_1_ID,
        participant1_name=PARTICIPANT_1_NAME,
        participant2_id=PARTICIPANT_2_ID,
        participant2_name=PARTICIPANT_2_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_score_confirmed(app: Flask, webhook_for_irc):
    expected_text = (
        'The result '
        'for match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8) '
        'has been confirmed.'
    )

    event = TourneyMatchScoreConfirmedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Octo-Highlander (8on8)',
        match_id=MATCH_ID,
        participant1_id=PARTICIPANT_1_ID,
        participant1_name=PARTICIPANT_1_NAME,
        participant2_id=PARTICIPANT_2_ID,
        participant2_name=PARTICIPANT_2_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_match_score_randomized(app: Flask, webhook_for_irc):
    expected_text = (
        'A random result has been entered '
        'for match "Die Einen" vs. "Die Anderen" '
        'in tourney Octo-Highlander (8on8).'
    )

    event = TourneyMatchScoreRandomizedEvent(
        occurred_at=now(),
        initiator_id=None,
        initiator_screen_name=None,
        tourney_id=TOURNEY_ID,
        tourney_title='Octo-Highlander (8on8)',
        match_id=MATCH_ID,
        participant1_id=PARTICIPANT_1_ID,
        participant1_name=PARTICIPANT_1_NAME,
        participant2_id=PARTICIPANT_2_ID,
        participant2_name=PARTICIPANT_2_NAME,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
