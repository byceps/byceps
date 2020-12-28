"""
byceps.announce.irc.util
~~~~~~~~~~~~~~~~~~~~~~~~

Send messages to an IRC bot (Weitersager_) via HTTP.

.. _Weitersager: https://github.com/homeworkprod/weitersager

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import current_app
import requests

from ...events.base import _BaseEvent
from ...services.webhooks import service as webhook_service
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..visibility import get_visibilities


def send_message(
    event: _BaseEvent, scope: str, scope_id: str, text: str
) -> None:
    """Write the text to the channel(s) configured for this event type
    by sending it to the bot via HTTP.
    """
    visibilities = get_visibilities(event)
    if not visibilities:
        current_app.logger.warning(
            f'No visibility assigned for event type "{type(event)}".'
        )
        return

    scope_id = None
    format = 'weitersager'

    webhooks = []
    for visibility in visibilities:
        scope = visibility.name

        webhooks.extend(
            webhook_service.get_enabled_outgoing_webhooks(
                scope, scope_id, format
            )
        )

    if not webhooks:
        current_app.logger.warning(
            f'No enabled IRC webhooks found. Not sending message to IRC.'
        )
        return

    # Stable order is easier to test.
    webhooks.sort(key=lambda wh: wh.extra_fields['channel'])

    for webhook in webhooks:
        call_webhook(webhook, text)


def call_webhook(webhook: OutgoingWebhook, text: str) -> None:
    text_prefix = webhook.text_prefix
    if text_prefix:
        text = text_prefix + text

    channel = webhook.extra_fields.get('channel')
    if not channel:
        current_app.logger.warning(f'No channel specified with IRC webhook.')
        return

    data = {'channel': channel, 'text': text}

    requests.post(webhook.url, json=data)  # Ignore response code for now.
