"""
byceps.announce.irc.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.tourney import (
    _TourneyEvent,
    TourneyStarted,
    TourneyPaused,
    TourneyCanceled,
    TourneyFinished,
    TourneyMatchReady,
    TourneyMatchReset,
    TourneyMatchScoreSubmitted,
    TourneyMatchScoreConfirmed,
    TourneyMatchScoreRandomized,
    TourneyParticipantReady,
    TourneyParticipantEliminated,
    TourneyParticipantWarned,
    TourneyParticipantDisqualified,
)

from ..common import tourney

from ._util import send_message


# -------------------------------------------------------------------- #
# tourney


def announce_tourney_started(event: TourneyStarted) -> None:
    text = tourney.assemble_text_for_tourney_started(event)

    send_tourney_message(event, text)


def announce_tourney_paused(event: TourneyPaused) -> None:
    text = tourney.assemble_text_for_tourney_paused(event)

    send_tourney_message(event, text)


def announce_tourney_canceled(event: TourneyCanceled) -> None:
    text = tourney.assemble_text_for_tourney_canceled(event)

    send_tourney_message(event, text)


def announce_tourney_finished(event: TourneyFinished) -> None:
    text = tourney.assemble_text_for_tourney_finished(event)

    send_tourney_message(event, text)


# -------------------------------------------------------------------- #
# match


def announce_match_ready(event: TourneyMatchReady) -> None:
    # Do not announce a match if it does not actually need to be played.
    if None in {event.participant1_id, event.participant2_id}:
        return

    text = tourney.assemble_text_for_match_ready(event)

    send_tourney_message(event, text)


def announce_match_reset(event: TourneyMatchReset) -> None:
    text = tourney.assemble_text_for_match_reset(event)

    send_tourney_message(event, text)


def announce_match_score_submitted(event: TourneyMatchScoreSubmitted) -> None:
    text = tourney.assemble_text_for_match_score_submitted(event)

    send_tourney_message(event, text)


def announce_match_score_confirmed(event: TourneyMatchScoreConfirmed) -> None:
    text = tourney.assemble_text_for_match_score_confirmed(event)

    send_tourney_message(event, text)


def announce_match_score_randomized(event: TourneyMatchScoreRandomized) -> None:
    text = tourney.assemble_text_for_match_score_randomized(event)

    send_tourney_message(event, text)


# -------------------------------------------------------------------- #
# participant


def announce_participant_ready(event: TourneyParticipantReady) -> None:
    text = tourney.assemble_text_for_participant_ready(event)

    send_tourney_message(event, text)


def announce_participant_eliminated(
    event: TourneyParticipantEliminated,
) -> None:
    text = tourney.assemble_text_for_participant_eliminated(event)

    send_tourney_message(event, text)


def announce_participant_warned(event: TourneyParticipantWarned) -> None:
    text = tourney.assemble_text_for_participant_warned(event)

    send_tourney_message(event, text)


def announce_participant_disqualified(
    event: TourneyParticipantDisqualified,
) -> None:
    text = tourney.assemble_text_for_participant_disqualified(event)

    send_tourney_message(event, text)


# -------------------------------------------------------------------- #
# helpers


def send_tourney_message(event: _TourneyEvent, text: str) -> None:
    scope = 'tourney'
    scope_id = event.tourney_id

    send_message(event, scope, scope_id, text)
