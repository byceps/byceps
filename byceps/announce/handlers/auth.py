"""
byceps.announce.handlers.auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce auth events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.auth import UserLoggedIn
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import auth


def announce_user_logged_in(
    event: UserLoggedIn, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user has logged in."""
    text = auth.assemble_text_for_user_logged_in(event)

    return Announcement(text)
