"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.tourney import (
    TourneyMatchReadyEvent,
    TourneyMatchResetEvent,
    TourneyMatchScoreConfirmedEvent,
    TourneyMatchScoreRandomizedEvent,
    TourneyMatchScoreSubmittedEvent,
)

from tests.helpers import generate_token, generate_uuid

from .helpers import build_announcement_request_for_irc, now


OCCURRED_AT = now()
TOURNEY_ID = str(generate_uuid())
MATCH_ID = str(generate_uuid())
PARTICIPANT_1_ID = generate_token()
PARTICIPANT_1_NAME = 'Die Einen'
PARTICIPANT_2_ID = generate_token()
PARTICIPANT_2_NAME = 'Die Anderen'


def test_announce_match_ready(app: Flask, webhook_for_irc):
    expected_text = (
        'Das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'kann gespielt werden.'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_reset(app: Flask, webhook_for_irc):
    expected_text = (
        'Das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde zurückgesetzt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_score_submitted(app: Flask, webhook_for_irc):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde ein Ergebnis eingetragen.'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_score_confirmed(app: Flask, webhook_for_irc):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde das eingetragene Ergebnis bestätigt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_score_randomized(app: Flask, webhook_for_irc):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde ein zufälliges Ergebnis eingetragen.'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected
