"""
byceps.services.webhooks.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, NewType
from uuid import UUID


WebhookID = NewType('WebhookID', UUID)


EventFilters = dict[str, dict[str, list[str]] | None]


@dataclass(frozen=True)
class OutgoingWebhook:
    id: WebhookID
    event_types: set[str]
    event_filters: EventFilters
    format: str
    text_prefix: str | None
    extra_fields: dict[str, Any]
    url: str
    description: str | None
    enabled: bool


@dataclass(frozen=True)
class Announcement:
    text: str
    announce_at: datetime | None = None


@dataclass(frozen=True)
class AnnouncementRequest:
    webhook_id: WebhookID
    url: str
    data: dict[str, Any]
    expected_response_status_code: int | None
    announce_at: datetime | None = None
