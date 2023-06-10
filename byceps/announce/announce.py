"""
byceps.announce.announce
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from http import HTTPStatus
from typing import Any

from flask import current_app
import requests

from byceps.events.base import _BaseEvent
from byceps.services.webhooks import webhook_service
from byceps.services.webhooks.models import AnnouncementRequest, OutgoingWebhook
from byceps.util.jobqueue import enqueue_at

from .events import get_name_for_event


class WebhookError(Exception):
    pass


def get_webhooks(event: _BaseEvent) -> list[OutgoingWebhook]:
    event_name = get_name_for_event(event)
    webhooks = webhook_service.get_enabled_outgoing_webhooks(event_name)

    # Stable order is easier to test.
    webhooks.sort(key=lambda wh: wh.extra_fields.get('channel', ''))

    return webhooks


def assemble_announcement_request(
    webhook: OutgoingWebhook, text: str, *, announce_at: datetime | None = None
) -> AnnouncementRequest:
    data = _assemble_request_data(webhook, text)
    return AnnouncementRequest(
        webhook_id=webhook.id,
        url=webhook.url,
        data=data,
        announce_at=announce_at,
    )


def _assemble_request_data(
    webhook: OutgoingWebhook, text: str
) -> dict[str, Any]:
    text_prefix = webhook.text_prefix
    if text_prefix:
        text = text_prefix + text

    if webhook.format == 'discord':
        return {'content': text}

    elif webhook.format == 'weitersager':
        channel = webhook.extra_fields.get('channel')
        if not channel:
            current_app.logger.warning('No channel specified with IRC webhook.')

        return {'channel': channel, 'text': text}

    elif webhook.format == 'mattermost':
        return {'text': text}

    elif webhook.format == 'matrix':
        key = webhook.extra_fields.get('key')
        if not key:
            current_app.logger.warning(
                'No API key specified with Matrix webhook.'
            )

        room_id = webhook.extra_fields.get('room_id')
        if not room_id:
            current_app.logger.warning(
                'No room ID specified with Matrix webhook.'
            )

        return {'key': key, 'room_id': room_id, 'text': text}

    else:
        return {}


def announce(
    webhook: OutgoingWebhook,
    announcement_request: AnnouncementRequest,
) -> None:
    announce_at = announcement_request.announce_at
    if announce_at is not None:
        # Schedule job to announce later.
        enqueue_at(announce_at, call_webhook, webhook, announcement_request)
    else:
        # Announce now.
        call_webhook(webhook, announcement_request)


def call_webhook(
    webhook: OutgoingWebhook,
    announcement_request: AnnouncementRequest,
) -> None:
    """Send HTTP request to the webhook."""
    response = requests.post(
        announcement_request.url, json=announcement_request.data, timeout=10
    )

    expected_response_code = EXPECTED_RESPONSE_STATUS_CODES.get(webhook.format)
    if expected_response_code is None:
        return

    actual_response_code = response.status_code
    if actual_response_code != expected_response_code:
        raise WebhookError(
            f'Endpoint for webhook {announcement_request.webhook_id} '
            f'returned unexpected status code {actual_response_code}'
        )


EXPECTED_RESPONSE_STATUS_CODES = {
    'discord': HTTPStatus.NO_CONTENT,
    'mattermost': HTTPStatus.OK,
    'matrix': HTTPStatus.OK,
    'weitersager': HTTPStatus.ACCEPTED,
}
