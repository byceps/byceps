"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Dict, Optional

from flask import current_app
import requests

from ..events.base import _BaseEvent
from ..services.webhooks import service as webhook_service
from ..services.webhooks.transfer.models import OutgoingWebhook

from .visibility import get_visibilities


def get_screen_name_or_fallback(screen_name: Optional[str]) -> str:
    """Return the screen name or a fallback value."""
    return screen_name if screen_name else 'Jemand'


def send_message(
    event: _BaseEvent, webhook_format: str, scope: str, scope_id: str, text: str
) -> None:
    """Send text to a webhook API."""
    if webhook_format == 'discord':
        # Send messages to Discord channels via its webhooks API.
        # The webhook URL already includes the (encoded) target channel.

        webhooks = webhook_service.get_enabled_outgoing_webhooks(
            scope, scope_id, webhook_format
        )
        if not webhooks:
            current_app.logger.warning(
                f'No enabled Discord webhook found for scope "{scope}" and '
                f'scope ID "{scope_id}". Not sending message to Discord.'
            )
            return

    elif webhook_format == 'weitersager':
        # Send messages to an IRC bot (Weitersager
        # <https://github.com/homeworkprod/weitersager>) via HTTP.

        visibilities = get_visibilities(event)
        if not visibilities:
            current_app.logger.warning(
                f'No visibility assigned for event type "{type(event)}".'
            )
            return

        scope_id = None

        webhooks = []
        for visibility in visibilities:
            scope = visibility.name

            webhooks.extend(
                webhook_service.get_enabled_outgoing_webhooks(
                    scope, scope_id, webhook_format
                )
            )

        if not webhooks:
            current_app.logger.warning(
                f'No enabled IRC webhooks found. Not sending message to IRC.'
            )
            return

        # Stable order is easier to test.
        webhooks.sort(key=lambda wh: wh.extra_fields['channel'])

    else:
        return

    for webhook in webhooks:
        call_webhook(webhook, text)


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
