"""
byceps.announce.irc.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
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
from ...signals import tourney as tourney_signals
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ._config import CHANNEL_PUBLIC


CHANNEL = CHANNEL_PUBLIC


# -------------------------------------------------------------------- #
# tourney


@tourney_signals.tourney_started.connect
def _on_tourney_started(sender, *, event: Optional[TourneyStarted] = None):
    enqueue(announce_tourney_started, event)


def announce_tourney_started(event: TourneyStarted):
    text = f'Das Turnier {event.tourney_title} wurde gestartet.'

    send_message(CHANNEL, text)


@tourney_signals.tourney_paused.connect
def _on_tourney_paused(sender, *, event: Optional[TourneyPaused] = None):
    enqueue(announce_tourney_paused, event)


def announce_tourney_paused(event: TourneyPaused):
    text = f'Das Turnier {event.tourney_title} wurde unterbrochen.'

    send_message(CHANNEL, text)


@tourney_signals.tourney_canceled.connect
def _on_tourney_canceled(sender, *, event: Optional[TourneyCanceled] = None):
    enqueue(announce_tourney_canceled, event)


def announce_tourney_canceled(event: TourneyCanceled):
    text = f'Das Turnier {event.tourney_title} wurde abgesagt.'

    send_message(CHANNEL, text)


@tourney_signals.tourney_finished.connect
def _on_tourney_finished(sender, *, event: Optional[TourneyFinished] = None):
    enqueue(announce_tourney_finished, event)


def announce_tourney_finished(event: TourneyFinished):
    text = f'Das Turnier {event.tourney_title} wurde beendet.'

    send_message(CHANNEL, text)


# -------------------------------------------------------------------- #
# match


@tourney_signals.match_ready.connect
def _on_match_ready(sender, *, event: Optional[TourneyMatchReady] = None):
    enqueue(announce_match_ready, event)


def announce_match_ready(event: TourneyMatchReady):
    # Do not announce a match if it does not actually need to be played.
    if None in {event.participant1_id, event.participant2_id}:
        return

    text = (
        f'Das Match {get_match_label(event)} im Turnier {event.tourney_title} '
        f'kann gespielt werden.'
    )

    send_message(CHANNEL, text)


@tourney_signals.match_reset.connect
def _on_match_reset(sender, *, event: Optional[TourneyMatchReset] = None):
    enqueue(announce_match_reset, event)


def announce_match_reset(event: TourneyMatchReset):
    text = (
        f'Das Match {get_match_label(event)} im Turnier {event.tourney_title} '
        f'wurde zurückgesetzt.'
    )

    send_message(CHANNEL, text)


@tourney_signals.match_score_submitted.connect
def _on_match_score_submitted(
    sender, *, event: Optional[TourneyMatchScoreSubmitted] = None
):
    enqueue(announce_match_score_submitted, event)


def announce_match_score_submitted(event: TourneyMatchScoreSubmitted):
    text = (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde ein Ergebnis eingetragen.'
    )

    send_message(CHANNEL, text)


@tourney_signals.match_score_confirmed.connect
def _on_match_score_confirmed(
    sender, *, event: Optional[TourneyMatchScoreConfirmed] = None
):
    enqueue(announce_match_score_confirmed, event)


def announce_match_score_confirmed(event: TourneyMatchScoreConfirmed):
    text = (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde das eingetragene Ergebnis bestätigt.'
    )

    send_message(CHANNEL, text)


@tourney_signals.match_score_randomized.connect
def _on_match_score_randomized(
    sender, *, event: Optional[TourneyMatchScoreRandomized] = None
):
    enqueue(announce_match_score_randomized, event)


def announce_match_score_randomized(event: TourneyMatchScoreRandomized):
    text = (
        f'Für das Match {get_match_label(event)} '
        f'im Turnier {event.tourney_title} '
        f'wurde ein zufälliges Ergebnis eingetragen.'
    )

    send_message(CHANNEL, text)


# -------------------------------------------------------------------- #
# participant


@tourney_signals.participant_ready.connect
def _on_participant_ready(
    sender, *, event: Optional[TourneyParticipantReady] = None
):
    enqueue(announce_participant_ready, event)


def announce_participant_ready(event: TourneyParticipantReady):
    text = (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        'ist spielbereit.'
    )

    send_message(CHANNEL, text)


@tourney_signals.participant_eliminated.connect
def _on_participant_eliminated(
    sender, *, event: Optional[TourneyParticipantEliminated] = None
):
    enqueue(announce_participant_eliminated, event)


def announce_participant_eliminated(event: TourneyParticipantEliminated):
    text = (
        f'"{event.participant_name}" scheidet aus dem Turnier '
        f'{event.tourney_title} aus.'
    )

    send_message(CHANNEL, text)


@tourney_signals.participant_warned.connect
def _on_participant_warned(
    sender, *, event: Optional[TourneyParticipantWarned] = None
):
    enqueue(announce_participant_warned, event)


def announce_participant_warned(event: TourneyParticipantWarned):
    text = (
        f'"{event.participant_name}" im Turnier {event.tourney_title} '
        f'hat eine gelbe Karte \x038,8 \x03 erhalten.'
    )

    send_message(CHANNEL, text)


@tourney_signals.participant_disqualified.connect
def _on_participant_disqualified(
    sender, *, event: Optional[TourneyParticipantDisqualified] = None
):
    enqueue(announce_participant_disqualified, event)


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
