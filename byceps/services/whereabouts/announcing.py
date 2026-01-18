"""
byceps.services.whereabouts.announcing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce whereabouts events.

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook

from .events import (
    WhereaboutsClientApprovedEvent,
    WhereaboutsClientDeletedEvent,
    WhereaboutsClientRegisteredEvent,
    WhereaboutsClientSignedOffEvent,
    WhereaboutsClientSignedOnEvent,
    WhereaboutsStatusUpdatedEvent,
    WhereaboutsUnknownTagDetectedEvent,
)


# client


@with_locale
def announce_whereabouts_client_registered(
    event_name: str,
    event: WhereaboutsClientRegisteredEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has been registered."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        'Whereabouts client "%(client_id)s" has been registered.',
        initiator_screen_name=initiator_screen_name,
        client_id=event.client_id,
    )

    return Announcement(text)


@with_locale
def announce_whereabouts_client_approved(
    event_name: str,
    event: WhereaboutsClientApprovedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has been approved."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has approved whereabouts client "%(client_id)s".',
        initiator_screen_name=initiator_screen_name,
        client_id=event.client_id,
    )

    return Announcement(text)


@with_locale
def announce_whereabouts_client_deleted(
    event_name: str,
    event: WhereaboutsClientDeletedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has deleted whereabouts client "%(client_id)s".',
        initiator_screen_name=initiator_screen_name,
        client_id=event.client_id,
    )

    return Announcement(text)


@with_locale
def announce_whereabouts_client_signed_on(
    event_name: str,
    event: WhereaboutsClientSignedOnEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has signed on."""
    text = gettext(
        'Whereabouts client "%(client_id)s" has signed on.',
        client_id=event.client_id,
    )

    return Announcement(text)


@with_locale
def announce_whereabouts_client_signed_off(
    event_name: str,
    event: WhereaboutsClientSignedOffEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a whereabouts client has signed off."""
    text = gettext(
        'Whereabouts client "%(client_id)s" has signed off.',
        client_id=event.client_id,
    )

    return Announcement(text)


# tag


@with_locale
def announce_whereabouts_unknown_tag_detected(
    event_name: str,
    event: WhereaboutsUnknownTagDetectedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that an unknown tag has been detected."""
    text = gettext(
        'Unknown tag "%(tag_identifier)s" has been detected by whereabouts '
        'client "%(client_id)s" at location "%(client_location)s".',
        client_id=event.client_id,
        client_location=event.client_location,
        tag_identifier=event.tag_identifier,
    )

    return Announcement(text)


# status


@with_locale
def announce_whereabouts_status_updated(
    event_name: str,
    event: WhereaboutsStatusUpdatedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a user's whereabouts has been updated."""
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(user_screen_name)s\'s whereabouts changed to "%(whereabouts_description)s".',
        user_screen_name=user_screen_name,
        whereabouts_description=event.whereabouts_description,
    )

    return Announcement(text)
