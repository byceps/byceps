"""
byceps.services.webhooks.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Dict, List, Optional

from ...database import db

from .models import OutgoingWebhook as DbOutgoingWebhook
from .transfer.models import EventSelectors, OutgoingWebhook, WebhookID


def create_outgoing_webhook(
    event_selectors: EventSelectors,
    scope: str,
    scope_id: Optional[str],
    format: str,
    url: str,
    enabled: bool,
    *,
    text_prefix: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> OutgoingWebhook:
    """Create an outgoing webhook."""
    webhook = DbOutgoingWebhook(
        event_selectors,
        scope,
        scope_id,
        format,
        url,
        enabled,
        text_prefix=text_prefix,
        extra_fields=extra_fields,
    )

    db.session.add(webhook)
    db.session.commit()

    return _db_entity_to_outgoing_webhook(webhook)


def delete_outgoing_webhook(webhook_id: WebhookID) -> None:
    """Delete the outgoing webhook."""
    db.session.query(DbOutgoingWebhook) \
        .filter_by(id=webhook_id) \
        .delete()
    db.session.commit()


def get_enabled_outgoing_webhooks(event_type: str) -> List[OutgoingWebhook]:
    """Return the configurations for enabled outgoing webhooks for that
    event type.
    """
    webhooks = db.session.query(DbOutgoingWebhook) \
        .filter(DbOutgoingWebhook.event_selectors.has_key(event_type)) \
        .all()

    return [_db_entity_to_outgoing_webhook(webhook) for webhook in webhooks]


def _db_entity_to_outgoing_webhook(
    webhook: DbOutgoingWebhook,
) -> OutgoingWebhook:
    event_selectors = (
        dict(webhook.event_selectors)
        if (webhook.event_selectors is not None)
        else {}
    )

    extra_fields = (
        dict(webhook.extra_fields) if (webhook.extra_fields is not None) else {}
    )

    return OutgoingWebhook(
        webhook.id,
        event_selectors,
        webhook.scope,
        webhook.scope_id,
        webhook.format,
        webhook.text_prefix,
        extra_fields,
        webhook.url,
        webhook.enabled,
    )
