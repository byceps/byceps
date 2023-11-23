"""
byceps.announce.handlers.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce guest server events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.guest_server import (
    GuestServerApprovedEvent,
    GuestServerCheckedInEvent,
    GuestServerCheckedOutEvent,
    GuestServerRegisteredEvent,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_guest_server_registered(
    event_name: str, event: GuestServerRegisteredEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a guest server has been registered."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    owner_screen_name = get_screen_name_or_fallback(event.owner)

    text = gettext(
        '%(initiator_screen_name)s has registered a guest server '
        'owned by %(owner_screen_name)s for party %(party_title)s.',
        initiator_screen_name=initiator_screen_name,
        owner_screen_name=owner_screen_name,
        party_title=event.party_title,
    )

    return Announcement(text)


@with_locale
def announce_guest_server_approved(
    event_name: str, event: GuestServerApprovedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a guest server has been approved."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    owner_screen_name = get_screen_name_or_fallback(event.owner)

    text = gettext(
        '%(initiator_screen_name)s has approved a guest server owned by %(owner_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        owner_screen_name=owner_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_guest_server_checked_in(
    event_name: str, event: GuestServerCheckedInEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a guest server has been checked in."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    owner_screen_name = get_screen_name_or_fallback(event.owner)

    text = gettext(
        '%(initiator_screen_name)s has checked in a guest server owned by %(owner_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        owner_screen_name=owner_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_guest_server_checked_out(
    event_name: str, event: GuestServerCheckedOutEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a guest server has been checked out."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    owner_screen_name = get_screen_name_or_fallback(event.owner)

    text = gettext(
        '%(initiator_screen_name)s has checked out a guest server owned by %(owner_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        owner_screen_name=owner_screen_name,
    )

    return Announcement(text)
