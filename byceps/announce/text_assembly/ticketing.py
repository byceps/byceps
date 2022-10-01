"""
byceps.announce.text_assembly.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext, ngettext

from ...events.ticketing import TicketCheckedIn, TicketsSold
from ...services.ticketing import ticket_service

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_ticket_checked_in(event: TicketCheckedIn) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has checked in ticket "%(ticket_code)s", used by %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        ticket_code=event.ticket_code,
        user_screen_name=user_screen_name,
    )


@with_locale
def assemble_text_for_tickets_sold(event: TicketsSold) -> str:
    owner_screen_name = get_screen_name_or_fallback(event.owner_screen_name)
    sale_stats = ticket_service.get_ticket_sale_stats(event.party_id)

    return (
        ngettext(
            '%(owner_screen_name)s has paid %(quantity)s ticket.',
            '%(owner_screen_name)s has paid %(quantity)s tickets.',
            event.quantity,
            owner_screen_name=owner_screen_name,
            quantity=event.quantity,
        )
        + ' '
        + gettext(
            'Currently %(tickets_sold)s of %(tickets_max)s tickets have been paid.',
            tickets_sold=sale_stats.tickets_sold,
            tickets_max=sale_stats.tickets_max,
        )
    )
