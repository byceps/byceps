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
from ..helpers import send_message


def announce_ticket_checked_in(
    event: TicketCheckedIn, webhook_format: str
) -> None:
    """Announce that a ticket has been checked in."""
    text = ticketing.assemble_text_for_ticket_checked_in(event)

    send_ticketing_message(event, webhook_format, text)


def announce_tickets_sold(event: TicketsSold, webhook_format: str) -> None:
    """Announce that tickets have been sold."""
    text = ticketing.assemble_text_for_tickets_sold(event)

    send_ticketing_message(event, webhook_format, text)


# helpers


def send_ticketing_message(
    event: Union[TicketCheckedIn, TicketsSold], webhook_format: str, text: str
) -> None:
    scope = 'ticketing'
    scope_id = None

    send_message(event, webhook_format, scope, scope_id, text)
