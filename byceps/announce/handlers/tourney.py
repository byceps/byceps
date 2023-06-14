"""
byceps.announce.handlers.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce tourney events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import with_locale
from byceps.events.tourney import (
    TourneyCanceledEvent,
    TourneyFinishedEvent,
    TourneyMatchReadyEvent,
    TourneyMatchResetEvent,
    TourneyMatchScoreConfirmedEvent,
    TourneyMatchScoreRandomizedEvent,
    TourneyMatchScoreSubmittedEvent,
    TourneyParticipantDisqualifiedEvent,
    TourneyParticipantEliminatedEvent,
    TourneyParticipantReadyEvent,
    TourneyParticipantWarnedEvent,
    TourneyPausedEvent,
    TourneyStartedEvent,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


# -------------------------------------------------------------------- #
# tourney


@with_locale
def announce_tourney_started(
    event_name: str, event: TourneyStartedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    text = gettext(
        'Tourney %(tourney_title)s has been started.',
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_tourney_paused(
    event_name: str, event: TourneyPausedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    text = gettext(
        'Tourney %(tourney_title)s has been paused.',
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_tourney_canceled(
    event_name: str, event: TourneyCanceledEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    text = gettext(
        'Tourney %(tourney_title)s has been canceled.',
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_tourney_finished(
    event_name: str, event: TourneyFinishedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    text = gettext(
        'Tourney %(tourney_title)s has been finished.',
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


# -------------------------------------------------------------------- #
# match


@with_locale
def announce_match_ready(
    event_name: str, event: TourneyMatchReadyEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    # Do not announce a match if it does not actually need to be played.
    if None in {event.participant1_id, event.participant2_id}:
        return None

    text = gettext(
        'Match %(match_label)s in tourney %(tourney_title)s is ready to be played.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_match_reset(
    event_name: str, event: TourneyMatchResetEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    text = gettext(
        'Match %(match_label)s in tourney %(tourney_title)s has been reset.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_match_score_submitted(
    event_name: str,
    event: TourneyMatchScoreSubmittedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    text = gettext(
        'A result has been entered for match %(match_label)s in tourney %(tourney_title)s.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_match_score_confirmed(
    event_name: str,
    event: TourneyMatchScoreConfirmedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    text = gettext(
        'The result for match %(match_label)s in tourney %(tourney_title)s has been confirmed.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_match_score_randomized(
    event_name: str,
    event: TourneyMatchScoreRandomizedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    text = gettext(
        'A random result has been entered for match %(match_label)s in tourney %(tourney_title)s.',
        match_label=get_match_label(event),
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


# -------------------------------------------------------------------- #
# participant


@with_locale
def announce_participant_ready(
    event_name: str,
    event: TourneyParticipantReadyEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    text = gettext(
        '"%(participant_name)s" in tourney %(tourney_title)s is ready to play.',
        participant_name=event.participant_name,
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_participant_eliminated(
    event_name: str,
    event: TourneyParticipantEliminatedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    text = gettext(
        '"%(participant_name)s" has been eliminated from tourney %(tourney_title)s.',
        participant_name=event.participant_name,
        tourney_title=event.tourney_title,
    )

    return Announcement(text)


@with_locale
def announce_participant_warned(
    event_name: str,
    event: TourneyParticipantWarnedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    yellow_card_irc = ' \x038,8 \x03'

    text = (
        gettext(
            '"%(participant_name)s" in tourney %(tourney_title)s has been warned.',
            participant_name=event.participant_name,
            tourney_title=event.tourney_title,
        )
        + yellow_card_irc
    )

    return Announcement(text)


@with_locale
def announce_participant_disqualified(
    event_name: str,
    event: TourneyParticipantDisqualifiedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    red_card_irc = ' \x034,4 \x03'

    text = (
        gettext(
            '"%(participant_name)s" in tourney %(tourney_title)s has been disqualified.',
            participant_name=event.participant_name,
            tourney_title=event.tourney_title,
        )
        + red_card_irc
    )

    return Announcement(text)


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
    participant_id: str | None, participant_name: str | None
) -> str:
    if participant_id is None:
        return gettext('bye')

    if not participant_name:
        return '<unnamed>'

    return participant_name
