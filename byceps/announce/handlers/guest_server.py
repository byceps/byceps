"""
byceps.announce.handlers.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.guest_server import GuestServerRegistered
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..helpers import call_webhook
from ..text_assembly import guest_server


def announce_guest_server_registered(
    event: GuestServerRegistered, webhook: OutgoingWebhook
) -> None:
    """Announce that a guest server has been registered."""
    text = guest_server.assemble_text_for_guest_server_registered(event)

    call_webhook(webhook, text)
