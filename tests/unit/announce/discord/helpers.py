"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.announce.helpers import AnnouncementRequest
from byceps.services.webhooks.models import OutgoingWebhook, WebhookID

from tests.helpers import generate_uuid


def now() -> datetime:
    return datetime.utcnow()


def build_announcement_request_for_discord(content: str) -> AnnouncementRequest:
    return AnnouncementRequest({'content': content})


def build_webhook(
    event_types, event_filters, text_prefix: str, url: str
) -> OutgoingWebhook:
    return OutgoingWebhook(
        id=WebhookID(generate_uuid()),
        event_types=event_types,
        event_filters=event_filters,
        format='discord',
        text_prefix=text_prefix,
        extra_fields={},
        url=url,
        description='',
        enabled=True,
    )