"""
byceps.announce.handlers.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce guest server events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.guest_server import GuestServerRegistered
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import guest_server


def announce_guest_server_registered(
    event: GuestServerRegistered, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a guest server has been registered."""
    text = guest_server.assemble_text_for_guest_server_registered(event)
    return Announcement(text)
