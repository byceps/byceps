"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.announce.connections import build_announcement_request
from byceps.events.tourney import (
    TourneyMatchReadyEvent,
    TourneyMatchResetEvent,
    TourneyMatchScoreConfirmedEvent,
    TourneyMatchScoreRandomizedEvent,
    TourneyMatchScoreSubmittedEvent,
)

from tests.integration.announce.irc.helpers import (
    build_announcement_request_for_irc,
    now,
)


def test_announce_match_ready(admin_app, tourney, match, webhook_for_irc):
    expected_text = (
        'Das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'kann gespielt werden.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyMatchReadyEvent(
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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_reset(admin_app, tourney, match, webhook_for_irc):
    expected_text = (
        'Das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde zurückgesetzt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyMatchResetEvent(
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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_score_submitted(
    admin_app, tourney, match, webhook_for_irc
):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde ein Ergebnis eingetragen.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyMatchScoreSubmittedEvent(
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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_score_confirmed(
    admin_app, tourney, match, webhook_for_irc
):
    expected_text = (
        'Für das Match "Die Einen" vs. "Die Anderen" '
        'im Turnier Octo-Highlander (8on8) '
        'wurde das eingetragene Ergebnis bestätigt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = TourneyMatchScoreConfirmedEvent(
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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_match_score_randomized(
    admin_app, tourney, match, webhook_for_irc
):
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
        tourney_id=tourney.id,
        tourney_title=tourney.title,
        match_id=match.id,
        participant1_id=match.participant1_id,
        participant1_name=match.participant1_name,
        participant2_id=match.participant2_id,
        participant2_name=match.participant2_name,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


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
