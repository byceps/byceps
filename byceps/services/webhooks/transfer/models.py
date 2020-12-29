"""
byceps.services.webhooks.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Any, Dict, NewType, Optional, Set
from uuid import UUID


WebhookID = NewType('WebhookID', UUID)


@dataclass(frozen=True)
class OutgoingWebhook:
    id: WebhookID
    event_selectors: Set[str]
    scope: str
    scope_id: Optional[str]
    format: str
    text_prefix: Optional[str]
    extra_fields: Optional[Dict[str, Any]]
    url: str
    enabled: bool
