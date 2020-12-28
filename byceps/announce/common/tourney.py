"""
byceps.announce.common.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.tourney import (
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


# -------------------------------------------------------------------- #
# tourney


def assemble_text_for_tourney_started(event: TourneyStarted) -> str:
    return f'Das Turnier {event.tourney_title} wurde gestartet.'


def assemble_text_for_tourney_paused(event: TourneyPaused) -> str:
    return f'Das Turnier {event.tourney_title} wurde unterbrochen.'


def assemble_text_for_tourney_canceled(event: TourneyCanceled) -> str:
    return f'Das Turnier {event.tourney_title} wurde abgesagt.'


def assemble_text_for_tourney_finished(event: TourneyFinished) -> str:
    return f'Das Turnier {event.tourney_title} wurde beendet.'


# -------------------------------------------------------------------- #
# match


def assemble_text_for_match_ready(event: TourneyMatchReady) -> str:
    return (
        f'Das Match {get_match_label(event)} im Turnier {event.tourney_title} '
        f'kann gespielt werden.'
    )


def assemble_text_for_match_reset(event: TourneyMatchReset) -> str:
    return (
        f'Das Match {get_match_label(event)} im Turnier {event.tourney_title} '
        f'wurde zurückgesetzt.'
    )


def assemble_text_for_match_score_submitted(
    event: TourneyMatchScoreSubmitted,
) -> str:
    return (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde ein Ergebnis eingetragen.'
    )


def assemble_text_for_match_score_confirmed(
    event: TourneyMatchScoreConfirmed,
) -> str:
    return (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde das eingetragene Ergebnis bestätigt.'
    )


def assemble_text_for_match_score_randomized(
    event: TourneyMatchScoreRandomized,
) -> str:
    return (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde ein zufälliges Ergebnis eingetragen.'
    )


# -------------------------------------------------------------------- #
# participant


def assemble_text_for_participant_ready(event: TourneyParticipantReady) -> str:
    return (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        'ist spielbereit.'
    )


def assemble_text_for_participant_eliminated(
    event: TourneyParticipantEliminated,
) -> str:
    return (
        f'"{event.participant_name}" scheidet aus dem Turnier '
        f'{event.tourney_title} aus.'
    )


def assemble_text_for_participant_warned(
    event: TourneyParticipantWarned,
) -> str:
    return (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        f'hat eine gelbe Karte \x038,8 \x03 erhalten.'
    )


def assemble_text_for_participant_disqualified(
    event: TourneyParticipantDisqualified,
) -> str:
    return (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        f'wurde disqualifiziert \x034,4 \x03.'
    )


# -------------------------------------------------------------------- #
# helpers


def get_match_label(match_event) -> str:
    participant1_label = get_participant_label(
        match_event.participant1_id, match_event.participant1_name
    )
    participant2_label = get_participant_label(
        match_event.participant2_id, match_event.participant2_name
    )

    return f'"{participant1_label}" vs. "{participant2_label}"'


def get_participant_label(
    participant_id: Optional[str], participant_name: Optional[str]
) -> str:
    if participant_id is None:
        return 'freilos'

    return participant_name
