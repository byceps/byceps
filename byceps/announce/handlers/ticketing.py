"""
byceps.announce.handlers.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import ticketing


def announce_ticket_checked_in(
    event: TicketCheckedIn, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a ticket has been checked in."""
    text = ticketing.assemble_text_for_ticket_checked_in(event)
    return Announcement(text)


def announce_tickets_sold(
    event: TicketsSold, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that tickets have been sold."""
    text = ticketing.assemble_text_for_tickets_sold(event)
    return Announcement(text)
