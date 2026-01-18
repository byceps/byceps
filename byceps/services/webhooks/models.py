"""
byceps.services.webhooks.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, NewType
from uuid import UUID


WebhookID = NewType('WebhookID', UUID)


EventFilters = dict[str, dict[str, list[str]] | None]


OutgoingWebhookFormat = Enum(
    'OutgoingWebhookFormat',
    [
        'discord',
        'matrix_webhook',  # https://github.com/nim65s/matrix-webhook
        'mattermost',
        'weitersager',  # https://homework.nwsnet.de/releases/1cda/
    ],
)


_OUTGOING_WEBHOOK_FORMAT_LABELS = {
    OutgoingWebhookFormat.discord: 'Discord',
    OutgoingWebhookFormat.matrix_webhook: 'Matrix Webhook',
    OutgoingWebhookFormat.mattermost: 'Mattermost',
    OutgoingWebhookFormat.weitersager: 'Weitersager',
}


def get_outgoing_webhook_format_label(format: OutgoingWebhookFormat) -> str:
    """Return a label for the format."""
    return _OUTGOING_WEBHOOK_FORMAT_LABELS[format]


@dataclass(frozen=True, kw_only=True)
class OutgoingWebhook:
    id: WebhookID
    event_types: set[str]
    event_filters: EventFilters
    format: OutgoingWebhookFormat
    text_prefix: str | None
    extra_fields: dict[str, Any]
    url: str
    description: str | None
    enabled: bool


@dataclass(frozen=True)
class Announcement:
    text: str
    announce_at: datetime | None = None


@dataclass(frozen=True, kw_only=True)
class AnnouncementRequest:
    webhook_id: WebhookID
    url: str
    data: dict[str, Any]
    expected_response_status_code: int | None
    announce_at: datetime | None = None
