"""
byceps.services.webhooks.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, NewType, Optional
from uuid import UUID


WebhookID = NewType('WebhookID', UUID)


EventFilters = dict[str, Optional[dict[str, list[str]]]]


@dataclass(frozen=True)
class OutgoingWebhook:
    id: WebhookID
    event_types: set[str]
    event_filters: EventFilters
    format: str
    text_prefix: str | None
    extra_fields: dict[str, Any]
    url: str
    description: str
    enabled: bool


@dataclass(frozen=True)
class Announcement:
    text: str
    announce_at: datetime | None = None


@dataclass(frozen=True)
class AnnouncementRequest:
    url: str
    data: dict[str, Any]
    announce_at: datetime | None = None
