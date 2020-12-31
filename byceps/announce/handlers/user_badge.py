"""
byceps.announce.handlers.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.user_badge import UserBadgeAwarded
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..common import user_badge
from ..helpers import call_webhook


def announce_user_badge_awarded(
    event: UserBadgeAwarded, webhook: OutgoingWebhook
) -> None:
    """Announce that a badge has been awarded to a user."""
    text = user_badge.assemble_text_for_user_badge_awarded(event)

    send_user_badge_message(event, webhook, text)


# helpers


def send_user_badge_message(
    event: UserBadgeAwarded, webhook: OutgoingWebhook, text: str
) -> None:
    call_webhook(webhook, text)
