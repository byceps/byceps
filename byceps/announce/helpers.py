"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import wraps
from http import HTTPStatus
from typing import Any

from flask import current_app
from flask_babel import force_locale, gettext
import requests

from byceps.events.base import _BaseEvent
from byceps.services.webhooks import webhook_service
from byceps.services.webhooks.models import OutgoingWebhook
from byceps.util.l10n import get_default_locale

from .events import get_name_for_event


def get_screen_name_or_fallback(screen_name: str | None) -> str:
    """Return the screen name or a fallback value."""
    return screen_name if screen_name else gettext('Someone')


def with_locale(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        locale = get_default_locale()
        with force_locale(locale):
            return handler(*args, **kwargs)

    return wrapper


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
    if event_name not in webhook.event_types:
        # This should not happen as only webhooks supporting this
        # event type should have been selected before calling an
        # event announcement handler.
        return False

    event_filter = webhook.event_filters.get(event_name)
    if event_filter is None:
        return True

    allowed_values = event_filter.get(attribute_name)
    return (allowed_values is None) or (actual_value in allowed_values)


def call_webhook(
    webhook: OutgoingWebhook, request_data: dict[str, Any]
) -> None:
    """Send HTTP request to the webhook."""
    response = requests.post(webhook.url, json=request_data, timeout=10)

    _check_response_status_code(webhook, response.status_code)


def assemble_request_data(
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
