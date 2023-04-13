"""
byceps.announce.handlers.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events.

:Copyright: 2014-2023 Jochen Kupperschmidt
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
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import tourney


# -------------------------------------------------------------------- #
# tourney


def announce_tourney_started(
    event: TourneyStarted, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_tourney_started(event)
    return Announcement(text)


def announce_tourney_paused(
    event: TourneyPaused, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_tourney_paused(event)
    return Announcement(text)


def announce_tourney_canceled(
    event: TourneyCanceled, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_tourney_canceled(event)
    return Announcement(text)


def announce_tourney_finished(
    event: TourneyFinished, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_tourney_finished(event)
    return Announcement(text)


# -------------------------------------------------------------------- #
# match


def announce_match_ready(
    event: TourneyMatchReady, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    # Do not announce a match if it does not actually need to be played.
    if None in {event.participant1_id, event.participant2_id}:
        return None

    text = tourney.assemble_text_for_match_ready(event)
    return Announcement(text)


def announce_match_reset(
    event: TourneyMatchReset, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_match_reset(event)
    return Announcement(text)


def announce_match_score_submitted(
    event: TourneyMatchScoreSubmitted, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_match_score_submitted(event)
    return Announcement(text)


def announce_match_score_confirmed(
    event: TourneyMatchScoreConfirmed, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_match_score_confirmed(event)
    return Announcement(text)


def announce_match_score_randomized(
    event: TourneyMatchScoreRandomized, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_match_score_randomized(event)
    return Announcement(text)


# -------------------------------------------------------------------- #
# participant


def announce_participant_ready(
    event: TourneyParticipantReady, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_participant_ready(event)
    return Announcement(text)


def announce_participant_eliminated(
    event: TourneyParticipantEliminated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_participant_eliminated(event)
    return Announcement(text)


def announce_participant_warned(
    event: TourneyParticipantWarned, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_participant_warned(event)
    return Announcement(text)


def announce_participant_disqualified(
    event: TourneyParticipantDisqualified, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    text = tourney.assemble_text_for_participant_disqualified(event)
    return Announcement(text)
