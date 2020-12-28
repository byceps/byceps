"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Dict, Optional

from flask import current_app
import requests

from ..services.webhooks.transfer.models import OutgoingWebhook


def get_screen_name_or_fallback(screen_name: Optional[str]) -> str:
    """Return the screen name or a fallback value."""
    return screen_name if screen_name else 'Jemand'


def call_webhook(webhook: OutgoingWebhook, text: str) -> None:
    """Send HTTP request to the webhook."""
    text_prefix = webhook.text_prefix
    if text_prefix:
        text = text_prefix + text

    data = _assemble_request_data(webhook, text)

    requests.post(webhook.url, json=data)  # Ignore response code for now.


def _assemble_request_data(
    webhook: OutgoingWebhook, text: str
) -> Dict[str, Any]:
    if webhook.format == 'discord':
        return {'content': text}

    elif webhook.format == 'weitersager':
        channel = webhook.extra_fields.get('channel')
        if not channel:
            current_app.logger.warning(
                f'No channel specified with IRC webhook.'
            )

        return {'channel': channel, 'text': text}
