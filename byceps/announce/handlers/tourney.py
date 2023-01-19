"""
byceps.announce.handlers.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

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

from ..helpers import call_webhook
from ..text_assembly import tourney


# -------------------------------------------------------------------- #
# tourney


def announce_tourney_started(
    event: TourneyStarted, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_tourney_started(event)

    call_webhook(webhook, text)


def announce_tourney_paused(
    event: TourneyPaused, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_tourney_paused(event)

    call_webhook(webhook, text)


def announce_tourney_canceled(
    event: TourneyCanceled, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_tourney_canceled(event)

    call_webhook(webhook, text)


def announce_tourney_finished(
    event: TourneyFinished, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_tourney_finished(event)

    call_webhook(webhook, text)


# -------------------------------------------------------------------- #
# match


def announce_match_ready(
    event: TourneyMatchReady, webhook: OutgoingWebhook
) -> None:
    # Do not announce a match if it does not actually need to be played.
    if None in {event.participant1_id, event.participant2_id}:
        return

    text = tourney.assemble_text_for_match_ready(event)

    call_webhook(webhook, text)


def announce_match_reset(
    event: TourneyMatchReset, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_match_reset(event)

    call_webhook(webhook, text)


def announce_match_score_submitted(
    event: TourneyMatchScoreSubmitted, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_match_score_submitted(event)

    call_webhook(webhook, text)


def announce_match_score_confirmed(
    event: TourneyMatchScoreConfirmed, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_match_score_confirmed(event)

    call_webhook(webhook, text)


def announce_match_score_randomized(
    event: TourneyMatchScoreRandomized, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_match_score_randomized(event)

    call_webhook(webhook, text)


# -------------------------------------------------------------------- #
# participant


def announce_participant_ready(
    event: TourneyParticipantReady, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_participant_ready(event)

    call_webhook(webhook, text)


def announce_participant_eliminated(
    event: TourneyParticipantEliminated, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_participant_eliminated(event)

    call_webhook(webhook, text)


def announce_participant_warned(
    event: TourneyParticipantWarned, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_participant_warned(event)

    call_webhook(webhook, text)


def announce_participant_disqualified(
    event: TourneyParticipantDisqualified, webhook: OutgoingWebhook
) -> None:
    text = tourney.assemble_text_for_participant_disqualified(event)

    call_webhook(webhook, text)
