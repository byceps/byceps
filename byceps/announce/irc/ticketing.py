"""
byceps.announce.irc.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...events.ticketing import TicketCheckedIn
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
