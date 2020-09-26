"""
byceps.services.webhooks.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType, Optional
from uuid import UUID


WebhookID = NewType('WebhookID', UUID)


@dataclass(frozen=True)
class OutgoingWebhook:
    id: WebhookID
    scope: str
    scope_id: Optional[str]
    format: str
    text_prefix: Optional[str]
    url: str
    enabled: bool
