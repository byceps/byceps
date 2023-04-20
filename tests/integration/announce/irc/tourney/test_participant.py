"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.announce.connections import build_announcement_request
from byceps.events.tourney import (
    TourneyParticipantDisqualified,
    TourneyParticipantEliminated,
    TourneyParticipantReady,
    TourneyParticipantWarned,
)

from tests.integration.announce.irc.helpers import (
    build_announcement_request_for_irc,
    now,
)


def test_announce_participant_ready(
    admin_app, tourney, match, participant, webhook_for_irc
):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) ist spielbereit.'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_participant_eliminated(
    admin_app, tourney, match, participant, webhook_for_irc
):
    expected_text = '"Le Supern00bs" ist aus dem Turnier Burrito Blaster (3on3) ausgeschieden.'
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_participant_warned(
    admin_app, tourney, match, participant, webhook_for_irc
):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) '
        'wurde verwarnt. \x038,8 \x03'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_participant_disqualified(
    admin_app, tourney, match, participant, webhook_for_irc
):
    expected_text = (
        '"Le Supern00bs" im Turnier Burrito Blaster (3on3) '
        'wurde disqualifiziert. \x034,4 \x03'
    )
    expected = build_announcement_request_for_irc(expected_text)

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

    assert build_announcement_request(event, webhook_for_irc) == expected


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
