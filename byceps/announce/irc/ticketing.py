"""
byceps.announce.irc.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce ticketing events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...events.ticketing import TicketCheckedIn
from ...signals import ticketing as ticketing_signals
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG


@ticketing_signals.ticket_checked_in.connect
def _on_ticket_checked_in(sender, *, event: TicketCheckedIn) -> None:
    enqueue(announce_ticket_checked_in, event)


def announce_ticket_checked_in(event: TicketCheckedIn) -> None:
    """Announce that a ticket has been checked in."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat Ticket "{event.ticket_code}", '
        f'benutzt von {user_screen_name}, eingecheckt.'
    )

    send_message(channels, text)
