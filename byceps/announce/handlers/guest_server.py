"""
byceps.announce.handlers.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce guest server events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.guest_server import GuestServerRegistered
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import call_webhook
from ..text_assembly import guest_server


def announce_guest_server_registered(
    event: GuestServerRegistered, webhook: OutgoingWebhook
) -> None:
    """Announce that a guest server has been registered."""
    text = guest_server.assemble_text_for_guest_server_registered(event)

    call_webhook(webhook, text)
