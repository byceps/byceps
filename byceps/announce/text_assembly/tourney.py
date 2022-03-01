"""
byceps.announce.text_assembly.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask_babel import gettext

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

from ._helpers import with_locale


# -------------------------------------------------------------------- #
# tourney


@with_locale
def assemble_text_for_tourney_started(event: TourneyStarted) -> str:
    return gettext(
        'Tourney %(tourney_title)s has been started.',
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_tourney_paused(event: TourneyPaused) -> str:
    return gettext(
        'Tourney %(tourney_title)s has been paused.',
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_tourney_canceled(event: TourneyCanceled) -> str:
    return gettext(
        'Tourney %(tourney_title)s has been canceled.',
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_tourney_finished(event: TourneyFinished) -> str:
    return gettext(
        'Tourney %(tourney_title)s has been finished.',
        tourney_title=event.tourney_title,
    )


# -------------------------------------------------------------------- #
# match


@with_locale
def assemble_text_for_match_ready(event: TourneyMatchReady) -> str:
    return gettext(
        'Match %(match_label)s in tourney %(tourney_title)s is ready to be played.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_match_reset(event: TourneyMatchReset) -> str:
    return gettext(
        'Match %(match_label)s in tourney %(tourney_title)s has been reset.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_match_score_submitted(
    event: TourneyMatchScoreSubmitted,
) -> str:
    return gettext(
        'A result has been entered for match %(match_label)s in tourney %(tourney_title)s.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_match_score_confirmed(
    event: TourneyMatchScoreConfirmed,
) -> str:
    return gettext(
        'The result for match %(match_label)s in tourney %(tourney_title)s has been confirmed.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_match_score_randomized(
    event: TourneyMatchScoreRandomized,
) -> str:
    return gettext(
        'A random result has been entered for match %(match_label)s in tourney %(tourney_title)s.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )


# -------------------------------------------------------------------- #
# participant


@with_locale
def assemble_text_for_participant_ready(event: TourneyParticipantReady) -> str:
    return gettext(
        '"%(participant_name)s" in tourney %(tourney_title)s is ready to play.',
        participant_name=event.participant_name,
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_participant_eliminated(
    event: TourneyParticipantEliminated,
) -> str:
    return gettext(
        '"%(participant_name)s" has been eliminated from tourney %(tourney_title)s.',
        participant_name=event.participant_name,
        tourney_title=event.tourney_title,
    )


@with_locale
def assemble_text_for_participant_warned(
    event: TourneyParticipantWarned,
) -> str:
    yellow_card_irc = ' \x038,8 \x03'

    return (
        gettext(
            '"%(participant_name)s" in tourney %(tourney_title)s has been warned.',
            participant_name=event.participant_name,
            tourney_title=event.tourney_title,
        )
        + yellow_card_irc
    )


@with_locale
def assemble_text_for_participant_disqualified(
    event: TourneyParticipantDisqualified,
) -> str:
    red_card_irc = ' \x034,4 \x03'

    return (
        gettext(
            '"%(participant_name)s" in tourney %(tourney_title)s has been disqualified.',
            participant_name=event.participant_name,
            tourney_title=event.tourney_title,
        )
        + red_card_irc
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

    return gettext(
        '"%(participant1_label)s" vs. "%(participant2_label)s"',
        participant1_label=participant1_label,
        participant2_label=participant2_label,
    )


def get_participant_label(
    participant_id: Optional[str], participant_name: Optional[str]
) -> str:
    if participant_id is None:
        return gettext('bye')

    if not participant_name:
        return '<unnamed>'

    return participant_name
