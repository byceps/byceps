"""
byceps.announce.discord.util
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send messages to Discord channels via its webhooks API.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import current_app
import requests

from ...services.webhooks import service as webhook_service


def send_message(scope: str, scope_id: str, text: str) -> None:
    """Send text to the webhook API.

    The endpoint URL already includes the target channel.
    """
    format = 'discord'
    webhook = webhook_service.find_enabled_outgoing_webhook(scope, scope_id, format)
    if webhook is None:
        current_app.logger.warning(
            f'No enabled Discord webhook found for scope "{scope}" and '
            f'scope ID "{scope_id}". Not sending message to Discord.'
        )
        return

    text_prefix = webhook.text_prefix
    if text_prefix:
        text = text_prefix + text

    data = {'content': text}

    requests.post(webhook.url, json=data)  # Ignore response code for now.
