"""
byceps.services.ticketing.announcing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events.

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext, ngettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.services.party import party_service
from byceps.services.webhooks.models import Announcement, OutgoingWebhook

from . import ticket_service
from .events import TicketCheckedInEvent, TicketsSoldEvent


@with_locale
def announce_ticket_checked_in(
    event_name: str, event: TicketCheckedInEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a ticket has been checked in."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has checked in ticket "%(ticket_code)s", used by %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        ticket_code=event.ticket_code,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_tickets_sold(
    event_name: str, event: TicketsSoldEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that tickets have been sold."""
    owner_screen_name = get_screen_name_or_fallback(event.owner)

    party = party_service.get_party(event.party.id)
    sale_stats = ticket_service.get_ticket_sale_stats(party)

    text = (
        ngettext(
            '%(owner_screen_name)s has paid for %(quantity)s ticket.',
            '%(owner_screen_name)s has paid for %(quantity)s tickets.',
            event.quantity,
            owner_screen_name=owner_screen_name,
            quantity=event.quantity,
        )
        + ' '
    )

    if sale_stats.tickets_max is not None:
        text += gettext(
            'Currently %(tickets_sold)s of %(tickets_max)s tickets have been sold.',
            tickets_sold=sale_stats.tickets_sold,
            tickets_max=sale_stats.tickets_max,
        )
    else:
        text += gettext(
            'Currently %(tickets_sold)s tickets have been sold.',
            tickets_sold=sale_stats.tickets_sold,
        )

    return Announcement(text)
