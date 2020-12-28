"""
byceps.announce.irc.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Union

from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...services.ticketing import ticket_service

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG
from ._util import send_message


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

    send_ticketing_message(event, CHANNEL_ORGA_LOG, text)


def announce_tickets_sold(event: TicketsSold) -> None:
    """Announce that ticket have been sold."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    owner_screen_name = get_screen_name_or_fallback(event.owner_screen_name)
    sale_stats = ticket_service.get_ticket_sale_stats(event.party_id)

    text = (
        f'{owner_screen_name} hat {event.quantity} Ticket(s) bezahlt. '
        f'Aktuell sind {sale_stats.tickets_sold} '
        f'von {sale_stats.tickets_max} Tickets bezahlt.'
    )

    send_ticketing_message(event, CHANNEL_ORGA_LOG, text)


# helpers


def send_ticketing_message(
    event: Union[TicketCheckedIn, TicketsSold], channel: str, text: str
) -> None:
    scope = 'ticketing'
    scope_id = None

    send_message(event, scope, scope_id, channel, text)
