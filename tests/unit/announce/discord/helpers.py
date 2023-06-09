"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.services.webhooks.models import (
    AnnouncementRequest,
    OutgoingWebhook,
    WebhookID,
)

from tests.helpers import generate_uuid


def now() -> datetime:
    return datetime.utcnow()


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


def assert_text(actual: AnnouncementRequest | None, expected_text: str) -> None:
    assert actual is not None
    assert actual.data == {'content': expected_text}
