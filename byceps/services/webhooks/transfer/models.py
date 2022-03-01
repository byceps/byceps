"""
byceps.services.webhooks.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, NewType, Optional
from uuid import UUID


WebhookID = NewType('WebhookID', UUID)


EventFilters = Dict[str, Optional[Dict[str, List[str]]]]


@dataclass(frozen=True)
class OutgoingWebhook:
    id: WebhookID
    event_types: set[str]
    event_filters: EventFilters
    format: str
    text_prefix: Optional[str]
    extra_fields: dict[str, Any]
    url: str
    description: str
    enabled: bool
