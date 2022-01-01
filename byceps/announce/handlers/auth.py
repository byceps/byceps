"""
byceps.announce.handlers.auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce auth events.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.auth import UserLoggedIn
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..helpers import call_webhook
from ..text_assembly import auth


def announce_user_logged_in(
    event: UserLoggedIn, webhook: OutgoingWebhook
) -> None:
    """Announce that a user has logged in."""
    text = auth.assemble_text_for_user_logged_in(event)

    call_webhook(webhook, text)
