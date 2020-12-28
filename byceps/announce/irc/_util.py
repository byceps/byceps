"""
byceps.announce.irc.util
~~~~~~~~~~~~~~~~~~~~~~~~

Send messages to an IRC bot (Weitersager_) via HTTP.

.. _Weitersager: https://github.com/homeworkprod/weitersager

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Set

from flask import current_app
import requests

from ...events.base import _BaseEvent
from ...services.webhooks import service as webhook_service
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..visibility import get_visibilities, Visibility

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


CHANNELS_BY_VISIBILITY = {
    Visibility.internal: CHANNEL_ORGA_LOG,
    Visibility.public: CHANNEL_PUBLIC,
}


def get_channels_for_event_type(event: _BaseEvent) -> Set[str]:
    """Return the channel(s) to announce this event on based on the
    event type's visibility.
    """
    visibilities = get_visibilities(event)
    return {CHANNELS_BY_VISIBILITY[visibility] for visibility in visibilities}


def send_message(
    event: _BaseEvent, scope: str, scope_id: str, text: str
) -> None:
    """Write the text to the channel(s) appropriate for this event type
    by sending it to the bot via HTTP.
    """
    channels = get_channels_for_event_type(event)
    if not channels:
        current_app.logger.warning(
            f'No IRC channels assigned for event type "{type(event)}".'
        )
        return

    scope = 'any'
    scope_id = None
    format = 'weitersager'

    webhook = webhook_service.find_enabled_outgoing_webhook(scope, scope_id, format)

    if webhook is None:
        current_app.logger.warning(
            f'No enabled IRC webhook found. Not sending message to IRC.'
        )
        return

    for channel in sorted(channels):  # Stable order is easier to test.
        call_webhook(webhook, channel, text)


def call_webhook(webhook: OutgoingWebhook, channel: str, text: str) -> None:
    text_prefix = webhook.text_prefix
    if text_prefix:
        text = text_prefix + text

    data = {'channel': channel, 'text': text}

    requests.post(webhook.url, json=data)  # Ignore response code for now.
