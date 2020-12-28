"""
byceps.announce.irc.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Union

from ...events.ticketing import TicketCheckedIn, TicketsSold

from ..common import ticketing

from ._util import send_message


def announce_ticket_checked_in(event: TicketCheckedIn) -> None:
    """Announce that a ticket has been checked in."""
    text = ticketing.assemble_text_for_ticket_checked_in(event)

    send_ticketing_message(event, text)


def announce_tickets_sold(event: TicketsSold) -> None:
    """Announce that tickets have been sold."""
    text = ticketing.assemble_text_for_tickets_sold(event)

    send_ticketing_message(event, text)


# helpers


def send_ticketing_message(
    event: Union[TicketCheckedIn, TicketsSold], text: str
) -> None:
    scope = 'ticketing'
    scope_id = None

    send_message(event, scope, scope_id, text)
