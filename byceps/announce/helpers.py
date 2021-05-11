"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from http import HTTPStatus
from typing import Any

from flask import current_app
import requests

from ..events.base import _BaseEvent
from ..services.webhooks import service as webhook_service
from ..services.webhooks.transfer.models import OutgoingWebhook

from .events import get_name_for_event


class WebhookError(Exception):
    pass


def get_webhooks(event: _BaseEvent) -> list[OutgoingWebhook]:
    event_name = get_name_for_event(event)
    webhooks = webhook_service.get_enabled_outgoing_webhooks(event_name)

    # Stable order is easier to test.
    webhooks.sort(key=lambda wh: wh.extra_fields.get('channel', ''))

    return webhooks


def matches_selectors(
    event: _BaseEvent,
    webhook: OutgoingWebhook,
    attribute_name: str,
    actual_value: str,
) -> bool:
    event_name = get_name_for_event(event)
    if event_name not in webhook.event_selectors:
        # This should not happen as only webhooks supporting this
        # event type should have been selected before calling an
        # event announcement handler.
        return False

    event_selector = webhook.event_selectors.get(event_name)
    if event_selector is None:
        # If no specific matcher rule is defined, a value of `None`
        # is okay (as it allows the event name to be contained in
        # the dictionary as a key).
        event_selector = {}

    allowed_values = event_selector.get(attribute_name)
    return (allowed_values is None) or (actual_value in allowed_values)


def call_webhook(webhook: OutgoingWebhook, text: str) -> None:
    """Send HTTP request to the webhook."""
    text_prefix = webhook.text_prefix
    if text_prefix:
        text = text_prefix + text

    data = _assemble_request_data(webhook, text)

    response = requests.post(webhook.url, json=data)

    _check_response_status_code(webhook, response.status_code)


def _assemble_request_data(
    webhook: OutgoingWebhook, text: str
) -> dict[str, Any]:
    if webhook.format == 'discord':
        return {'content': text}

    elif webhook.format == 'weitersager':
        channel = webhook.extra_fields.get('channel')
        if not channel:
            current_app.logger.warning(
                f'No channel specified with IRC webhook.'
            )

        return {'channel': channel, 'text': text}

    elif webhook.format == 'mattermost':
        return {'text': text}

    elif webhook.format == 'matrix':
        key = webhook.extra_fields.get('key')
        if not key:
            current_app.logger.warning(
                f'No API key specified with Matrix webhook.'
            )

        room_id = webhook.extra_fields.get('room_id')
        if not room_id:
            current_app.logger.warning(
                f'No room ID specified with Matrix webhook.'
            )

        return {'key': key, 'room_id': room_id, 'text': text}


EXPECTED_RESPONSE_STATUS_CODES = {
    'discord': HTTPStatus.NO_CONTENT,
    'mattermost': HTTPStatus.OK,
    'matrix': HTTPStatus.OK,
    'weitersager': HTTPStatus.ACCEPTED,
}


def _check_response_status_code(webhook: OutgoingWebhook, code: int) -> None:
    expected_code = EXPECTED_RESPONSE_STATUS_CODES.get(webhook.format)
    if expected_code is None:
        return

    if code != expected_code:
        raise WebhookError(
            f'Endpoint for webhook {webhook.id} '
            f'returned unexpected status code {code}'
        )
