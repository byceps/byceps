"""
byceps.announce.discord.util
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send messages to Discord channels via its webhooks API.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import current_app

from ...events.base import _BaseEvent
from ...services.webhooks import service as webhook_service

from ..helpers import call_webhook


def send_message(
    event: _BaseEvent, scope: str, scope_id: str, text: str
) -> None:
    """Send text to the webhook API.

    The endpoint URL already includes the target channel.
    """
    format = 'discord'
    webhooks = webhook_service.get_enabled_outgoing_webhooks(
        scope, scope_id, format
    )
    if not webhooks:
        current_app.logger.warning(
            f'No enabled Discord webhook found for scope "{scope}" and '
            f'scope ID "{scope_id}". Not sending message to Discord.'
        )
        return

    for webhook in webhooks:
        call_webhook(webhook, text)
