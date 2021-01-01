"""
byceps.announce.text_assembly.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...services.ticketing import ticket_service

from ._helpers import get_screen_name_or_fallback


def assemble_text_for_ticket_checked_in(event: TicketCheckedIn) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} hat Ticket "{event.ticket_code}", '
        f'benutzt von {user_screen_name}, eingecheckt.'
    )


def assemble_text_for_tickets_sold(event: TicketsSold) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    owner_screen_name = get_screen_name_or_fallback(event.owner_screen_name)
    sale_stats = ticket_service.get_ticket_sale_stats(event.party_id)

    return (
        f'{owner_screen_name} hat {event.quantity} Ticket(s) bezahlt. '
        f'Aktuell sind {sale_stats.tickets_sold} '
        f'von {sale_stats.tickets_max} Tickets bezahlt.'
    )
