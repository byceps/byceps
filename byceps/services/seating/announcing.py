"""
byceps.services.seating.announcing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce seating events.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from byceps.announce.helpers import get_screen_name_or_fallback, with_locale
from byceps.services.webhooks.models import Announcement, OutgoingWebhook

from .events import SeatGroupOccupiedEvent, SeatGroupReleasedEvent


@with_locale
def announce_seat_group_occupied(
    event_name: str, event: SeatGroupOccupiedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a seat group has been occupied."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    ticket_bundle_owner_screen_name = get_screen_name_or_fallback(
        event.ticket_bundle_owner
    )

    text = gettext(
        '%(initiator_screen_name)s has occupied seat group "%(seat_group_title)s" with ticket bundle %(ticket_bundle_id)s owned by %(ticket_bundle_owner_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        seat_group_title=event.seat_group_title,
        ticket_bundle_id=event.ticket_bundle_id,
        ticket_bundle_owner_screen_name=ticket_bundle_owner_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_seat_group_released(
    event_name: str, event: SeatGroupReleasedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a seat group has been released."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has released seat group "%(seat_group_title)s".',
        initiator_screen_name=initiator_screen_name,
        seat_group_title=event.seat_group_title,
    )

    return Announcement(text)
