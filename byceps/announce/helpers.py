"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Dict, List, Optional

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
        webhooks = get_webhooks_for_discord(event, scope, scope_id)

    elif webhook_format == 'weitersager':
        # Send messages to an IRC bot (Weitersager
        # <https://github.com/homeworkprod/weitersager>) via HTTP.
        webhooks = get_webhooks_for_irc(event)

    else:
        return

    for webhook in webhooks:
        call_webhook(webhook, text)


def get_webhooks_for_discord(
    event: _BaseEvent, scope: str, scope_id: str
) -> List[OutgoingWebhook]:
    webhook_format = 'discord'
    webhooks = webhook_service.get_enabled_outgoing_webhooks(webhook_format)
    webhooks = select_webhooks(webhooks, scope, scope_id)

    if not webhooks:
        current_app.logger.warning(
            f'No enabled Discord webhook found for scope "{scope}" and '
            f'scope ID "{scope_id}". Not sending message to Discord.'
        )
        return []

    return webhooks


def get_webhooks_for_irc(event: _BaseEvent) -> List[OutgoingWebhook]:
    visibilities = get_visibilities(event)
    if not visibilities:
        current_app.logger.warning(
            f'No visibility assigned for event type "{type(event)}".'
        )
        return []

    scope_id = None
    webhook_format = 'weitersager'

    webhooks = []
    for visibility in visibilities:
        scope = visibility.name

        relevant_webhooks = webhook_service.get_enabled_outgoing_webhooks(
            webhook_format
        )
        relevant_webhooks = select_webhooks(relevant_webhooks, scope, scope_id)
        webhooks.extend(relevant_webhooks)

    if not webhooks:
        current_app.logger.warning(
            f'No enabled IRC webhooks found. Not sending message to IRC.'
        )
        return []

    # Stable order is easier to test.
    webhooks.sort(key=lambda wh: wh.extra_fields['channel'])

    return webhooks


def select_webhooks(
    webhooks: List[OutgoingWebhook], scope: str, scope_id: str
) -> List[OutgoingWebhook]:
    return [wh for wh in webhooks if match_scope(wh, scope, scope_id)]


def match_scope(webhook: OutgoingWebhook, scope: str, scope_id: str) -> bool:
    return webhook.scope == scope and webhook.scope_id == scope_id


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
