"""
byceps.announce.irc.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...services.ticketing import ticket_service
from ...signals import ticketing as ticketing_signals
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG
from ._util import send_message


@ticketing_signals.ticket_checked_in.connect
def _on_ticket_checked_in(
    sender, *, event: Optional[TicketCheckedIn] = None
) -> None:
    enqueue(announce_ticket_checked_in, event)


def announce_ticket_checked_in(event: TicketCheckedIn) -> None:
    """Announce that a ticket has been checked in."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat Ticket "{event.ticket_code}", '
        f'benutzt von {user_screen_name}, eingecheckt.'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@ticketing_signals.tickets_sold.connect
def _on_tickets_sold(sender, *, event: Optional[TicketsSold] = None) -> None:
    enqueue(announce_tickets_sold, event)


def announce_tickets_sold(event: TicketsSold) -> None:
    """Announce that ticket have been sold."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    owner_screen_name = get_screen_name_or_fallback(event.owner_screen_name)
    sale_stats = ticket_service.get_ticket_sale_stats(event.party_id)

    text = (
        f'{owner_screen_name} hat {event.quantity} Ticket(s) gekauft. '
        f'Aktuell sind {sale_stats.tickets_sold} '
        f'von {sale_stats.tickets_max} Tickets verkauft.'
    )

    send_message(CHANNEL_ORGA_LOG, text)
