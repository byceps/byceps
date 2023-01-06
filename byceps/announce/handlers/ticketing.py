"""
byceps.announce.handlers.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..helpers import call_webhook
from ..text_assembly import ticketing


def announce_ticket_checked_in(
    event: TicketCheckedIn, webhook: OutgoingWebhook
) -> None:
    """Announce that a ticket has been checked in."""
    text = ticketing.assemble_text_for_ticket_checked_in(event)

    call_webhook(webhook, text)


def announce_tickets_sold(event: TicketsSold, webhook: OutgoingWebhook) -> None:
    """Announce that tickets have been sold."""
    text = ticketing.assemble_text_for_tickets_sold(event)

    call_webhook(webhook, text)
