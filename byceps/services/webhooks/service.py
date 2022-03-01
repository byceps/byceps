"""
byceps.services.webhooks.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Any, Optional

from ...database import db

from .dbmodels import OutgoingWebhook as DbOutgoingWebhook
from .transfer.models import EventFilters, OutgoingWebhook, WebhookID


def create_outgoing_webhook(
    event_types: set[str],
    event_filters: EventFilters,
    format: str,
    url: str,
    enabled: bool,
    *,
    text_prefix: Optional[str] = None,
    extra_fields: Optional[dict[str, Any]] = None,
    description: Optional[str] = None,
) -> OutgoingWebhook:
    """Create an outgoing webhook."""
    webhook = DbOutgoingWebhook(
        event_types,
        event_filters,
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
    event_types: set[str],
    event_filters: EventFilters,
    format: str,
    text_prefix: Optional[str],
    extra_fields: Optional[dict[str, Any]],
    url: str,
    description: Optional[str],
    enabled: bool,
) -> OutgoingWebhook:
    """Update an outgoing webhook."""
    webhook = _find_db_webhook(webhook_id)
    if webhook is None:
        raise ValueError(f'Unknown webhook ID "{webhook_id}"')

    webhook.event_types = event_types
    webhook.event_filters = event_filters
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
    return db.session.get(DbOutgoingWebhook, webhook_id)


def get_all_webhooks() -> list[OutgoingWebhook]:
    """Return all webhooks."""
    webhooks = db.session.query(DbOutgoingWebhook).all()

    return [_db_entity_to_outgoing_webhook(webhook) for webhook in webhooks]


def get_enabled_outgoing_webhooks(event_type: str) -> list[OutgoingWebhook]:
    """Return the configurations for enabled outgoing webhooks for that
    event type.
    """
    webhooks = db.session.query(DbOutgoingWebhook) \
        .filter(DbOutgoingWebhook._event_types.contains([event_type])) \
        .filter_by(enabled=True) \
        .all()

    return [_db_entity_to_outgoing_webhook(webhook) for webhook in webhooks]


def _db_entity_to_outgoing_webhook(
    webhook: DbOutgoingWebhook,
) -> OutgoingWebhook:
    event_filters = (
        dict(webhook.event_filters)
        if (webhook.event_filters is not None)
        else {}
    )

    extra_fields = (
        dict(webhook.extra_fields) if (webhook.extra_fields is not None) else {}
    )

    return OutgoingWebhook(
        id=webhook.id,
        event_types=webhook.event_types,
        event_filters=event_filters,
        format=webhook.format,
        text_prefix=webhook.text_prefix,
        extra_fields=extra_fields,
        url=webhook.url,
        description=webhook.description,
        enabled=webhook.enabled,
    )
