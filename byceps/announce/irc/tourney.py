"""
byceps.announce.irc.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events on IRC.

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

from ._config import CHANNEL_PUBLIC
from ._util import send_message


CHANNEL = CHANNEL_PUBLIC


# -------------------------------------------------------------------- #
# tourney


def announce_tourney_started(event: TourneyStarted):
    text = f'Das Turnier {event.tourney_title} wurde gestartet.'

    send_message(CHANNEL, text)


def announce_tourney_paused(event: TourneyPaused):
    text = f'Das Turnier {event.tourney_title} wurde unterbrochen.'

    send_message(CHANNEL, text)


def announce_tourney_canceled(event: TourneyCanceled):
    text = f'Das Turnier {event.tourney_title} wurde abgesagt.'

    send_message(CHANNEL, text)


def announce_tourney_finished(event: TourneyFinished):
    text = f'Das Turnier {event.tourney_title} wurde beendet.'

    send_message(CHANNEL, text)


# -------------------------------------------------------------------- #
# match


def announce_match_ready(event: TourneyMatchReady):
    # Do not announce a match if it does not actually need to be played.
    if None in {event.participant1_id, event.participant2_id}:
        return

    text = (
        f'Das Match {get_match_label(event)} im Turnier {event.tourney_title} '
        f'kann gespielt werden.'
    )

    send_message(CHANNEL, text)


def announce_match_reset(event: TourneyMatchReset):
    text = (
        f'Das Match {get_match_label(event)} im Turnier {event.tourney_title} '
        f'wurde zurückgesetzt.'
    )

    send_message(CHANNEL, text)


def announce_match_score_submitted(event: TourneyMatchScoreSubmitted):
    text = (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde ein Ergebnis eingetragen.'
    )

    send_message(CHANNEL, text)


def announce_match_score_confirmed(event: TourneyMatchScoreConfirmed):
    text = (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde das eingetragene Ergebnis bestätigt.'
    )

    send_message(CHANNEL, text)


def announce_match_score_randomized(event: TourneyMatchScoreRandomized):
    text = (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde ein zufälliges Ergebnis eingetragen.'
    )

    send_message(CHANNEL, text)


# -------------------------------------------------------------------- #
# participant


def announce_participant_ready(event: TourneyParticipantReady):
    text = (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        'ist spielbereit.'
    )

    send_message(CHANNEL, text)


def announce_participant_eliminated(event: TourneyParticipantEliminated):
    text = (
        f'"{event.participant_name}" scheidet aus dem Turnier '
        f'{event.tourney_title} aus.'
    )

    send_message(CHANNEL, text)


def announce_participant_warned(event: TourneyParticipantWarned):
    text = (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        f'hat eine gelbe Karte \x038,8 \x03 erhalten.'
    )

    send_message(CHANNEL, text)


def announce_participant_disqualified(event: TourneyParticipantDisqualified):
    text = (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        f'wurde disqualifiziert \x034,4 \x03.'
    )

    send_message(CHANNEL, text)


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
