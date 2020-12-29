"""
byceps.announce.handlers.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Union

from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..common import ticketing
from ..helpers import call_webhook


def announce_ticket_checked_in(
    event: TicketCheckedIn, webhook: OutgoingWebhook
) -> None:
    """Announce that a ticket has been checked in."""
    text = ticketing.assemble_text_for_ticket_checked_in(event)

    send_ticketing_message(event, webhook, text)


def announce_tickets_sold(event: TicketsSold, webhook: OutgoingWebhook) -> None:
    """Announce that tickets have been sold."""
    text = ticketing.assemble_text_for_tickets_sold(event)

    send_ticketing_message(event, webhook, text)


# helpers


def send_ticketing_message(
    event: Union[TicketCheckedIn, TicketsSold],
    webhook: OutgoingWebhook,
    text: str,
) -> None:
    scope = 'ticketing'
    scope_id = None

    call_webhook(webhook, text)
