"""
byceps.services.webhooks.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Dict, List, Optional

from ...database import db

from .dbmodels import OutgoingWebhook as DbOutgoingWebhook
from .transfer.models import EventSelectors, OutgoingWebhook, WebhookID


def create_outgoing_webhook(
    event_selectors: EventSelectors,
    format: str,
    url: str,
    enabled: bool,
    *,
    text_prefix: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
) -> OutgoingWebhook:
    """Create an outgoing webhook."""
    webhook = DbOutgoingWebhook(
        event_selectors,
        format,
        url,
        enabled,
        text_prefix=text_prefix,
        extra_fields=extra_fields,
        description=description,
    )

    db.session.add(webhook)
    db.session.commit()

    return _db_entity_to_outgoing_webhook(webhook)


def update_outgoing_webhook(
    webhook_id: WebhookID,
    event_selectors: EventSelectors,
    format: str,
    url: str,
    enabled: bool,
    *,
    text_prefix: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
) -> OutgoingWebhook:
    """Update an outgoing webhook."""
    webhook = _find_db_webhook(webhook_id)
    if webhook is None:
        raise ValueError(f'Unknown webhook ID "{webhook_id}"')

    webhook.event_selectors = event_selectors
    webhook.format = format
    webhook.text_prefix = text_prefix
    webhook.extra_fields = extra_fields
    webhook.url = url
    webhook.description = description
    webhook.enabled = enabled

    db.session.commit()

    return _db_entity_to_outgoing_webhook(webhook)


def delete_outgoing_webhook(webhook_id: WebhookID) -> None:
    """Delete the outgoing webhook."""
    db.session.query(DbOutgoingWebhook) \
        .filter_by(id=webhook_id) \
        .delete()
    db.session.commit()


def find_webhook(webhook_id: WebhookID) -> Optional[OutgoingWebhook]:
    """Return the webhook with that ID, if found."""
    webhook = _find_db_webhook(webhook_id)

    if webhook is None:
        return None

    return _db_entity_to_outgoing_webhook(webhook)


def _find_db_webhook(webhook_id: WebhookID) -> Optional[DbOutgoingWebhook]:
    """Return the webhook database entity with that ID, if found."""
    return db.session.query(DbOutgoingWebhook).get(webhook_id)


def get_all_webhooks() -> List[OutgoingWebhook]:
    """Return all webhooks."""
    webhooks = db.session.query(DbOutgoingWebhook).all()

    return [_db_entity_to_outgoing_webhook(webhook) for webhook in webhooks]


def get_enabled_outgoing_webhooks(event_type: str) -> List[OutgoingWebhook]:
    """Return the configurations for enabled outgoing webhooks for that
    event type.
    """
    webhooks = db.session.query(DbOutgoingWebhook) \
        .filter(DbOutgoingWebhook.event_selectors.has_key(event_type)) \
        .filter_by(enabled=True) \
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
        webhook.format,
        webhook.text_prefix,
        extra_fields,
        webhook.url,
        webhook.description,
        webhook.enabled,
    )
